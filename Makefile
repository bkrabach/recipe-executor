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
	@recipe-executor recipes/recipe_executor/create.json

# Edit/revise the existing recipe executor code using the recipe executor itself
.PHONY: recipe-executor-edit
recipe-executor-edit:
	@echo "Revising the existing recipe executor code from recipe..."
	@recipe-executor recipes/recipe_executor/edit.json
