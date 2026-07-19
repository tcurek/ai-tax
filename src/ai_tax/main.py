from ai_tax.agents import run_hello_world_agent
from ai_tax.config import load_config


def main() -> None:
    """Run the hello-world agent app."""
    config = load_config()
    message = run_hello_world_agent()

    print(message)
    print(f"Source tax documents dir: {config.source_tax_documents_dir}")


if __name__ == "__main__":
    main()
