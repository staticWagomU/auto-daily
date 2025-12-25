{
  description = "auto-daily - macOS window activity logger with Ollama daily report generation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem [ "aarch64-darwin" "x86_64-darwin" ] (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

      in
      {
        devShells.default = pkgs.mkShell {
          name = "auto-daily-dev";

          buildInputs = [
            pkgs.python312
            pkgs.uv
            pkgs.ruff
            pkgs.lefthook
          ];

          shellHook = ''
            # Sync dependencies with uv
            if [ ! -d .venv ] || [ pyproject.toml -nt .venv ]; then
              echo "Syncing dependencies with uv..."
              uv sync
            fi

            source .venv/bin/activate

            # Install lefthook if not installed
            if [ ! -f .git/hooks/pre-commit ] || ! grep -q "lefthook" .git/hooks/pre-commit 2>/dev/null; then
              echo "Installing lefthook..."
              lefthook install
            fi

            echo ""
            echo "🚀 auto-daily development environment"
            echo ""
            echo "Python: $(python --version)"
            echo "uv:     $(uv --version)"
            echo "Ruff:   $(ruff --version)"
            echo ""
            echo "Available commands:"
            echo "  uv sync               # Sync dependencies"
            echo "  pytest tests/ -v      # Run tests"
            echo "  ruff check .          # Lint"
            echo "  ruff format .         # Format"
            echo "  ty check src/         # Type check"
            echo ""
          '';

          # Environment variables
          PYTHONDONTWRITEBYTECODE = "1";
          PYTHONUNBUFFERED = "1";
        };
      }
    );
}
