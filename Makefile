repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Build AI context files for the recipe executor
.PHONY: ai-context-files
ai-context-files:
	@echo "Building AI context files for recipe executor development..."
	@python $(repo_root)/tools/build_ai_context_files.py
	@python $(repo_root)/tools/build_git_collector_files.py

.PHONY: recipe-executor-create recipe-executor-edit create-component edit-component

# Create recipe executor code from scratch using modular recipes
recipe-executor-create:
	@echo "Generating recipe executor code from modular recipes..."
	recipe-tool --execute recipes/recipe_executor/build.json model=openai/o4-mini

# Edit existing recipe executor code using modular recipes
recipe-executor-edit:
	@echo "Editing recipe executor code from modular recipes..."
	recipe-tool --execute recipes/recipe_executor/build.json model=openai/o4-mini edit=true existing_code_root=.

# Create a specific component
create-component:
	@echo "Generating component $(COMPONENT)..."
	recipe-tool --execute recipes/recipe_executor/build.json model=openai/o4-mini component_id=$(COMPONENT)

# Edit a specific component
edit-component:
	@echo "Editing component $(COMPONENT)..."
	recipe-tool --execute recipes/recipe_executor/build.json model=openai/o4-mini component_id=$(COMPONENT) edit=true existing_code_root=.

# Usage examples:
# make create-component COMPONENT=context
# make edit-component COMPONENT=llm_utils.llm
