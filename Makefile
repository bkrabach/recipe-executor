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
