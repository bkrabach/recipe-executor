repo_root = $(shell git rev-parse --show-toplevel)
include $(repo_root)/tools/makefiles/python.mk

# Build AI context files for the recipe executor
.PHONY: recipe-executor-context
recipe-executor-context:
	@echo "Building AI context files for recipe executor development..."
	@python $(repo_root)/tools/build_ai_context_files.py

# Create new recipe executor code from scratch using the recipe executor itself
.PHONY: recipe-executor-create
recipe-executor-create:
	@echo "Generating recipe executor code from scratch from recipe..."
	@python recipe_executor/main.py recipes/recipe_executor/create.json

# Create with description and optional directories
.PHONY: recipe-executor-create-with-desc
recipe-executor-create-with-desc:
	@if [ -z "$(DESC)" ]; then \
		echo "Error: DESC is required. Usage: make recipe-executor-create-with-desc DESC=\"Your product description\" [IN=\"/path/to/input\"] [OUT=\"/path/to/output\"]"; \
		exit 1; \
	fi
	@echo "Generating recipe executor code with custom description..."
	@python recipe_executor/main.py recipes/recipe_executor/create.json "$(DESC)" $(if $(IN),-i "$(IN)") $(if $(OUT),-o "$(OUT)")

# Edit/revise the existing recipe executor code using the recipe executor itself
.PHONY: recipe-executor-edit
recipe-executor-edit:
	@echo "Revising the existing recipe executor code from recipe..."
	@python recipe_executor/main.py recipes/recipe_executor/edit.json

# User-friendly interactive terminal UI
.PHONY: run
run:
	@clear
	@echo "======================================================"
	@echo "🚀 Recipe Executor - Interactive Terminal UI"
	@echo "======================================================"
	@echo ""
	@echo "MAIN MENU"
	@echo ""
	@echo "Code Generation:"
	@echo "  1) 🏗️  Generate code from recipe-executor templates"
	@echo "  2) ✏️  Edit existing code using recipe-executor"
	@echo ""
	@echo "Blueprint Operations:"
	@echo "  3) 📝 Create component blueprint"
	@echo "  4) 🧩 Generate code from blueprint"
	@echo ""
	@echo "Recipe Utilities:"
	@echo "  5) 📋 Execute custom recipe file"
	@echo "  6) 🔍 List available recipes"
	@echo ""
	@echo "System Tools:"
	@echo "  7) 🔄 Rebuild AI context files"
	@echo "  8) ℹ️  View system information"
	@echo "  9) 🚪 Exit"
	@echo ""
	@echo "Enter your choice [1-9]: "
	@bash -c 'read choice; \
	case $$choice in \
		1) \
			clear; \
			echo "======================================================"; \
			echo "🏗️  Generate Code from Recipe-Executor Templates"; \
			echo "======================================================"; \
			echo ""; \
			echo "Enter details for code generation:"; \
			echo ""; \
			read -p "📋 Product Description: " description; \
			echo ""; \
			read -p "📁 Input Directory (optional, press Enter to skip): " input_dir; \
			echo ""; \
			read -p "💾 Output Directory (optional, press Enter to skip): " output_dir; \
			echo ""; \
			echo "🔄 Starting recipe execution..."; \
			echo "------------------------------------------------------"; \
			make recipe-executor-create-with-desc DESC="$$description" $$([ -n "$$input_dir" ] && echo "IN=\"$$input_dir\"") $$([ -n "$$output_dir" ] && echo "OUT=\"$$output_dir\""); \
			echo "------------------------------------------------------"; \
			echo "✅ Execution complete!"; \
			;; \
		2) \
			clear; \
			echo "======================================================"; \
			echo "✏️  Edit Existing Code Using Recipe-Executor"; \
			echo "======================================================"; \
			echo ""; \
			echo "🔄 Running recipe editor..."; \
			echo "------------------------------------------------------"; \
			make recipe-executor-edit; \
			echo "------------------------------------------------------"; \
			echo "✅ Edit complete!"; \
			;; \
		3) \
			clear; \
			echo "======================================================"; \
			echo "📝 Create Component Blueprint"; \
			echo "======================================================"; \
			echo ""; \
			echo "This will guide you through creating a component blueprint."; \
			echo ""; \
			read -p "📋 Component Name: " component_name; \
			echo ""; \
			read -p "📋 Component Description: " component_desc; \
			echo ""; \
			read -p "💾 Output Directory (optional, press Enter to use default): " output_dir; \
			echo ""; \
			echo "🔄 Creating component blueprint..."; \
			echo "------------------------------------------------------"; \
			python recipe_executor/main.py recipes/component_blueprint_generator/create.json "$$component_desc" $$([ -n "$$output_dir" ] && echo "-o $$output_dir") -c "component_name=$$component_name"; \
			echo "------------------------------------------------------"; \
			echo "✅ Blueprint creation complete!"; \
			;; \
		4) \
			clear; \
			echo "======================================================"; \
			echo "🧩 Generate Code from Blueprint"; \
			echo "======================================================"; \
			echo ""; \
			echo "This will generate code from an existing blueprint."; \
			echo ""; \
			read -p "📋 Blueprint Path: " blueprint_path; \
			echo ""; \
			read -p "💾 Output Directory (optional, press Enter to use default): " output_dir; \
			echo ""; \
			echo "🔄 Generating code from blueprint..."; \
			echo "------------------------------------------------------"; \
			python recipe_executor/main.py recipes/codebase_generator/generate_code.json -c "spec_path=$$blueprint_path" $$([ -n "$$output_dir" ] && echo "-o $$output_dir"); \
			echo "------------------------------------------------------"; \
			echo "✅ Code generation complete!"; \
			;; \
		5) \
			clear; \
			echo "======================================================"; \
			echo "📋 Execute Custom Recipe File"; \
			echo "======================================================"; \
			echo ""; \
			echo "This will execute a custom recipe file."; \
			echo ""; \
			read -p "📋 Recipe Path: " recipe_path; \
			echo ""; \
			read -p "📋 Description (optional): " description; \
			echo ""; \
			read -p "📁 Input Directory (optional, press Enter to skip): " input_dir; \
			echo ""; \
			read -p "💾 Output Directory (optional, press Enter to skip): " output_dir; \
			echo ""; \
			read -p "📋 Additional Context (key1=value1,key2=value2): " context_vars; \
			echo ""; \
			echo "🔄 Executing recipe..."; \
			echo "------------------------------------------------------"; \
			python recipe_executor/main.py "$$recipe_path" $$([ -n "$$description" ] && echo "\"$$description\"") \
				$$([ -n "$$input_dir" ] && echo "-i $$input_dir") $$([ -n "$$output_dir" ] && echo "-o $$output_dir") \
				$$([ -n "$$context_vars" ] && echo "$$context_vars" | sed -e "s/,/ -c /g" -e "s/^/-c /"); \
			echo "------------------------------------------------------"; \
			echo "✅ Recipe execution complete!"; \
			;; \
		6) \
			clear; \
			echo "======================================================"; \
			echo "🔍 List Available Recipes"; \
			echo "======================================================"; \
			echo ""; \
			echo "Available Recipes:"; \
			echo ""; \
			find recipes -type f -name "*.json" | sort | head -n 30 | sed "s/^/  - /"; \
			echo ""; \
			num_recipes=$$(find recipes -type f -name "*.json" | wc -l | xargs); \
			if [ $$num_recipes -gt 30 ]; then \
				echo "  ... and $$(expr $$num_recipes - 30) more recipes (showing first 30)"; \
			fi; \
			echo ""; \
			echo "To execute a recipe, choose option 5 from the main menu."; \
			;; \
		7) \
			clear; \
			echo "======================================================"; \
			echo "🔄 Rebuild AI Context Files"; \
			echo "======================================================"; \
			echo ""; \
			echo "🔄 Rebuilding files..."; \
			echo "------------------------------------------------------"; \
			make recipe-executor-context; \
			echo "------------------------------------------------------"; \
			echo "✅ Rebuild complete!"; \
			;; \
		8) \
			clear; \
			echo "======================================================"; \
			echo "ℹ️  System Information"; \
			echo "======================================================"; \
			echo ""; \
			echo "Recipe Executor System Information:"; \
			echo ""; \
			echo "📂 Project Directory: $$(pwd)"; \
			echo "🐍 Python Version: $$(python --version 2>&1)"; \
			echo "📦 Installed Packages:"; \
			python -m pip list | grep -E "jinja2|pydantic|openai|anthropic|liquid"; \
			echo ""; \
			echo "🗃️  Recipe Counts:"; \
			echo "  - Total Recipes: $$(find recipes -name "*.json" | wc -l | xargs)"; \
			echo "  - Codebase Generator Recipes: $$(find recipes/codebase_generator -name "*.json" | wc -l | xargs)"; \
			echo "  - Blueprint Generator Recipes: $$(find recipes/component_blueprint_generator -name "*.json" | wc -l | xargs)"; \
			echo "  - Recipe Executor Recipes: $$(find recipes/recipe_executor -name "*.json" | wc -l | xargs)"; \
			echo "  - Example Recipes: $$(find recipes/example_* -name "*.json" | wc -l | xargs 2>/dev/null || echo 0)"; \
			echo ""; \
			echo "🔧 Available Commands:"; \
			grep -E "^[a-zA-Z0-9_-]+:" Makefile | cut -d ":" -f 1 | sort | sed "s/^/  - make /"; \
			;; \
		9) \
			clear; \
			echo ""; \
			echo "👋 Goodbye! Have a great day!"; \
			echo ""; \
			exit 0; \
			;; \
		*) \
			echo ""; \
			echo "❌ Invalid choice. Please try again."; \
			exit 1; \
			;; \
	esac; \
	echo ""; \
	read -p "Press Enter to return to main menu" dummy; \
	make run'