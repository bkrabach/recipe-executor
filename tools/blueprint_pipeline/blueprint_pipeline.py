#!/usr/bin/env python3
"""
blueprint_pipeline/
├── __init__.py             # Package initialization
├── blueprint_pipeline.py   # Main entry point
├── component_processor.py  # Component processing logic
├── config.py               # Configuration handling
├── executor.py             # Step and recipe execution
├── flow_control.py         # Flow control and user interaction
├── generator.py            # Blueprint and code generation
└── utils.py                # Utility functions
"""

import argparse
import os
import sys
from datetime import datetime

from blueprint_pipeline.component_processor import (
    analyze_component_dependencies,
    determine_components_to_process,
    process_component_split,
    process_components_in_parallel,
    process_project_analysis,
)
from blueprint_pipeline.config import get_base_context, parse_args, setup_directories
from blueprint_pipeline.flow_control import ActionState, FlowControl, handle_human_review_feedback, pause_and_check
from blueprint_pipeline.generator import generate_blueprints_and_code_in_parallel
from blueprint_pipeline.utils import find_latest_spec, safe_print


def main():
    """Main entry point for the blueprint pipeline."""
    # Parse command line arguments
    args = parse_args()

    # Check for resume flag
    resume = "--resume" in sys.argv
    if resume:
        safe_print("Resume mode enabled. Will skip steps with existing output files.")

    # Initialize flow control mode
    if resume:
        flow_mode = FlowControl.RESUME
    elif args.auto:
        flow_mode = FlowControl.AUTO_MODE
    else:
        flow_mode = FlowControl.STEP_BY_STEP

    # Initialize action state for retries
    last_action = ActionState()

    # Create base context with common parameters
    base_context = get_base_context(args)

    # Create output directories
    setup_directories(args.output_dir, args.target_project)

    # Track completion status for components
    component_status = {}  # component_id -> "complete" or "needs_review"
    dependency_map = {}  # component_id -> list of component IDs it depends on

    iteration_count = 0
    all_complete = False

    # Check if we're resuming from a previous run
    if resume:
        # Determine highest iteration based on existing files
        for i in range(1, args.max_iterations + 1):
            if os.path.exists(f"{args.output_dir}/iteration_{i}_summary.txt"):
                iteration_count = i

        if iteration_count > 0:
            safe_print(f"Resuming from iteration {iteration_count}")

            # Load component status if available
            if os.path.exists(f"{args.output_dir}/component_status.txt"):
                with open(f"{args.output_dir}/component_status.txt", "r") as f:
                    for line in f:
                        if ":" in line:
                            comp_id, status = line.strip().split(":", 1)
                            component_status[comp_id] = status.strip()
                safe_print(f"Loaded status for {len(component_status)} components")

            # Load dependency map if available
            if os.path.exists(f"{args.output_dir}/dependency_map.txt"):
                with open(f"{args.output_dir}/dependency_map.txt", "r") as f:
                    for line in f:
                        if ":" in line:
                            comp_id, deps_str = line.strip().split(":", 1)
                            deps = [d.strip() for d in deps_str.strip().split(",") if d.strip()]
                            if deps:
                                dependency_map[comp_id] = deps
                safe_print(f"Loaded dependencies for {len(dependency_map)} components")

    while not all_complete and iteration_count < args.max_iterations:
        iteration_count += 1
        safe_print(f"\n=== Starting Iteration {iteration_count} ===")

        # Only run project analysis and split to components on first iteration
        if iteration_count == 1:
            # Step 1: Project Split Analysis
            result_flow_mode, last_action = process_project_analysis(args, base_context, flow_mode, last_action)

            # Return early if the step failed
            if result_flow_mode is None:
                return

            flow_mode = result_flow_mode

            # If retry requested, continue from the top of the loop
            if flow_mode == FlowControl.RETRY:
                continue

            # Step 2: Split to Components
            result_flow_mode, last_action = process_component_split(args, base_context, flow_mode, last_action)

            # Return early if the step failed
            if result_flow_mode is None:
                return

            flow_mode = result_flow_mode

            # If retry requested, continue from the top of the loop
            if flow_mode == FlowControl.RETRY:
                continue

        # Determine which components to process in this iteration and analyze dependencies
        component_specs, component_status, dependency_map = determine_components_to_process(
            args.output_dir, component_status, iteration_count, args.component_filter
        )

        # Log dependency information if verbose
        if args.verbose and dependency_map:
            safe_print("\n=== Component Dependencies ===")
            for comp_id, deps in dependency_map.items():
                if deps:
                    safe_print(f"{comp_id} depends on: {', '.join(deps)}")

        if not component_specs:
            if iteration_count == 1:
                safe_print("No component specifications were found to process. Exiting.")
                return
            else:
                safe_print("All components have been completed successfully.")
                all_complete = True
                continue

        safe_print(f"Processing {len(component_specs)} component specifications in iteration {iteration_count}.")

        # Process all components in parallel according to flow mode
        component_status, human_review_needed, flow_mode, last_action = process_components_in_parallel(
            component_specs,
            component_status,
            base_context,
            args.output_dir,
            args.verbose,
            flow_mode,
            args.max_workers,
            dependency_map,
        )

        # Save component status for possible future resume
        with open(f"{args.output_dir}/component_status.txt", "w") as f:
            for comp_id, status in component_status.items():
                f.write(f"{comp_id}: {status}\n")

        # Save dependency map for possible future resume
        with open(f"{args.output_dir}/dependency_map.txt", "w") as f:
            for comp_id, deps in dependency_map.items():
                if deps:
                    f.write(f"{comp_id}: {', '.join(deps)}\n")

        # Save iteration summary
        with open(f"{args.output_dir}/iteration_{iteration_count}_summary.txt", "w") as f:
            f.write(f"Iteration {iteration_count} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total components: {len(component_status)}\n")
            f.write(f"Components processed in this iteration: {len(component_specs)}\n")
            f.write(f"Components needing human review: {len(human_review_needed)}\n")

        # Check if any components need human review
        if human_review_needed:
            safe_print("\n=== Components Needing Human Review ===")
            for component_id, spec_path, reason in human_review_needed:
                safe_print(f"- {component_id}: {reason}")
                safe_print(f"  Spec: {spec_path}")
                safe_print(f"  Evaluation: {args.output_dir}/human_review/{component_id}*.md")

            # Update action state
            last_action = ActionState(
                step_name="Check For Components Needing Human Review",
                component_id=None,
                recipe_path="",
                context={},
            )

            # Pause after checking human review (unless in resume mode)
            if flow_mode != FlowControl.RESUME:
                flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True)

            # Handle human review feedback
            proceed, additional_context = handle_human_review_feedback()
            if not proceed:
                safe_print("Exiting pipeline at user request.")
                return

            # Update context files if provided
            if additional_context:
                if args.context_files:
                    args.context_files = f"{args.context_files},{additional_context}"
                else:
                    args.context_files = additional_context

                # Update base context
                base_context = get_base_context(args)

                # Update action state
                last_action = ActionState(
                    step_name="Process Human Review Input",
                    component_id=None,
                    recipe_path="",
                    context={},
                )

                # Pause after processing human input (unless in resume mode)
                if flow_mode != FlowControl.RESUME:
                    flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True)
        else:
            all_complete = all(status == "complete" for status in component_status.values())
            if all_complete:
                safe_print("\nAll components have been successfully processed!")

                # Update action state
                last_action = ActionState(
                    step_name="All Components Evaluated Successfully",
                    component_id=None,
                    recipe_path="",
                    context={},
                )

                # Pause before blueprint generation (unless in resume mode)
                if flow_mode != FlowControl.RESUME:
                    flow_mode = pause_and_check(flow_mode, last_action, allow_until_complete_option=True)
            else:
                safe_print("\nSome components still need processing in the next iteration.")

    # Check if we hit the max iterations
    if not all_complete:
        safe_print(f"\nReached maximum iterations ({args.max_iterations}) without completing all components.")
        safe_print("Please review remaining issues manually before proceeding.")
        return

    # Proceed to blueprint and code generation
    safe_print("\n=== Generating Blueprints and Code ===")

    # Get all successfully completed component specs
    completed_specs = []
    for component_id, status in component_status.items():
        if status == "complete":
            spec_path = find_latest_spec(component_id, args.output_dir)
            if spec_path:
                completed_specs.append((component_id, spec_path))

    # If no dependency map was created, do a final analysis before code generation
    if not dependency_map:
        dependency_map = analyze_component_dependencies(args.output_dir)

    # Generate blueprints and code in parallel
    successful_components, failed_components = generate_blueprints_and_code_in_parallel(
        completed_specs,
        dependency_map,
        base_context,
        args.output_dir,
        args.target_project,
        args.verbose,
        flow_mode,
        args.max_workers,
    )

    # Final Summary
    safe_print("\n=== Pipeline Summary ===")
    safe_print(f"Total components processed: {len(component_status)}")
    safe_print(f"Successfully completed components: {len([s for s in component_status.values() if s == 'complete'])}")
    safe_print(f"Successfully generated code for: {len(successful_components)} components")
    safe_print(f"Failed code generation for: {len(failed_components)} components")

    safe_print("\nComponent Status:")
    for component_id, status in component_status.items():
        safe_print(f"  - {component_id}: {status}")

    if successful_components:
        safe_print(f"\nGenerated code can be found in: {args.output_dir}/code/{args.target_project}")
        safe_print("\nSuccessfully generated blueprints and code for components:")
        for component_id in successful_components:
            safe_print(f"  - {component_id}")

    if failed_components:
        safe_print("\nFailed to generate blueprints or code for components:")
        for component_id in failed_components:
            safe_print(f"  - {component_id}")

    # Log completion time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_print(f"\nPipeline completed at: {timestamp}")

    # Save final status
    with open(f"{args.output_dir}/pipeline_complete.txt", "w") as f:
        f.write(f"Pipeline completed at: {timestamp}\n")
        f.write(f"Total components: {len(component_status)}\n")
        f.write(
            f"Successfully completed components: {len([s for s in component_status.values() if s == 'complete'])}\n"
        )
        f.write(f"Successfully generated code for: {len(successful_components)} components\n")
        f.write(f"Failed code generation for: {len(failed_components)} components\n")

    # Final pause (unless in resume mode)
    if flow_mode != FlowControl.AUTO_MODE and flow_mode != FlowControl.RESUME:
        input("\nPipeline complete. Press Enter to exit.")


def parse_args_with_resume() -> argparse.Namespace:
    """
    Parse command line arguments including the resume flag.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Blueprint-to-Code Generation Pipeline")

    # Required arguments
    parser.add_argument("--project_spec", required=True, help="Path to the project specification file")

    # Optional arguments
    parser.add_argument("--context_files", help="Comma-separated list of context files")
    parser.add_argument("--output_dir", default="output", help="Output directory")
    parser.add_argument("--model", default="openai:o3-mini", help="LLM model to use")
    parser.add_argument("--target_project", default="generated_project", help="Target project name")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--component_filter", help="Only process components matching this prefix")
    parser.add_argument("--max_iterations", type=int, default=3, help="Maximum number of refinement iterations")
    parser.add_argument("--auto", action="store_true", help="Run automatically without pausing")
    parser.add_argument("--max_workers", type=int, default=4, help="Maximum number of parallel workers")
    parser.add_argument("--resume", action="store_true", help="Resume from a previous execution")

    return parser.parse_args()


if __name__ == "__main__":
    main()
