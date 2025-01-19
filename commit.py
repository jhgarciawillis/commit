import os
import subprocess
import sys
from typing import List, Callable, Dict, Optional

class GitHubSetup:
    def __init__(self):
        self.project_directory: str = ''
        self.git_config = {
            'username': '',

            'email': '',
            'repository_url': '',
            'commit_message': ''
        }
        self.ignored_files: List[str] = []

    def run_shell_command(self, command: str) -> bool:
        """
        Execute a shell command and handle its output and errors.
        
        Args:
            command (str): Shell command to execute
        
        Returns:
            bool: True if command successful, False otherwise
        """
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as error:
            print(f"Command Execution Error: {error}")
            print(error.stderr)
            return False

    def validate_git_installation(self) -> bool:
        """
        Check if Git is installed on the system.
        
        Returns:
            bool: True if Git is installed, False otherwise
        """
        try:
            subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True
            )
            print("Git is already installed.")
            return True
        except FileNotFoundError:
            print("Git is not installed.")
            self.provide_git_installation_guidance()
            return False

    def provide_git_installation_guidance(self):
        """
        Provide installation instructions for Git across different platforms.
        """
        installation_guides = {
            'Windows': 'https://git-scm.com/download/win',
            'macOS': 'https://git-scm.com/download/mac',
            'Linux': 'sudo apt-get install git'
        }
        
        print("\n--- Git Installation Guide ---")
        for platform, link in installation_guides.items():
            print(f"{platform}: {link}")
        
        input("Press Enter after installing Git...")

    def select_project_directory(self) -> bool:
        """
        Prompt user to select or input project directory.
        
        Returns:
            bool: True if a valid directory is selected, False otherwise
        """
        while True:
            directory_input = input("Enter full project directory path (e.g., C:\\Users\\luisg\\Downloads\\Code\\Piano): ").strip()
            
            # Normalize the path and handle potential quotes
            directory_path = directory_input.strip('"\'')
            
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                try:
                    # Change current working directory
                    os.chdir(directory_path)
                    self.project_directory = directory_path
                    print(f"✅ Project directory set to: {self.project_directory}")
                    return True
                except Exception as e:
                    print(f"❌ Error changing directory: {e}")
            else:
                print("❌ Invalid directory. Please check the path and try again.")
                retry = input("Would you like to try again? (y/n): ").lower()
                if retry != 'y':
                    return False

    def check_existing_git_config(self) -> Optional[dict]:
        """
        Check existing Git configuration.
        
        Returns:
            Optional[dict]: Existing Git configuration or None
        """
        try:
            # Retrieve existing Git config
            username_cmd = subprocess.run(
                ['git', 'config', '--global', 'user.name'], 
                capture_output=True, 
                text=True
            )
            email_cmd = subprocess.run(
                ['git', 'config', '--global', 'user.email'], 
                capture_output=True, 
                text=True
            )
            
            # Check if commands were successful
            if username_cmd.returncode == 0 and email_cmd.returncode == 0:
                existing_config = {
                    'username': username_cmd.stdout.strip(),
                    'email': email_cmd.stdout.strip()
                }
                return existing_config
            return None
        except Exception as e:
            print(f"Error checking Git configuration: {e}")
            return None

    def configure_git_credentials(self):
        """
        Handle Git credentials configuration with existing config awareness.
        """
        existing_config = self.check_existing_git_config()
        
        if existing_config:
            print("\n--- Existing Git Configuration Found ---")
            print(f"Current Username: {existing_config['username']}")
            print(f"Current Email: {existing_config['email']}")
            
            choice = input("Do you want to (K)eep existing, (U)pdate, or (C)ancel? ").lower()
            
            if choice == 'k':
                # Keep existing configuration
                self.git_config['username'] = existing_config['username']
                self.git_config['email'] = existing_config['email']
                print("✅ Existing Git configuration retained.")
                return
            elif choice == 'c':
                print("Git configuration setup cancelled.")
                return
        
        # Proceed with new configuration
        while True:
            self.git_config['username'] = input("Enter Git Username: ").strip()
            self.git_config['email'] = input("Enter Git Email: ").strip()
            
            username_cmd = f'git config --global user.name "{self.git_config["username"]}"'
            email_cmd = f'git config --global user.email "{self.git_config["email"]}"'
            
            if (self.run_shell_command(username_cmd) and 
                self.run_shell_command(email_cmd)):
                print("✅ Git credentials configured successfully!")
                break
            else:
                print("❌ Configuration failed. Retry...")

    def create_comprehensive_gitignore(self):
        """
        Create a comprehensive .gitignore with multiple configuration options.
        """
        predefined_ignores = {
            '1': ['node_modules/', '*.log', '.DS_Store'],
            '2': ['*.pyc', '__pycache__/', '.venv/', 'venv/'],
            '3': ['*.class', 'target/', 'build/'],
            '4': ['.idea/', '.vscode/', '*.sublime-project', '*.sublime-workspace'],
            '5': ['*.swp', '*.swo', '*~']
        }

        print("\n--- .gitignore Configuration ---")
        print("Select predefined .gitignore templates (multiple choices allowed):")
        for key, ignores in predefined_ignores.items():
            print(f"{key}. {', '.join(ignores)}")
        print("6. Custom manual entry")
        print("7. Skip .gitignore creation")

        selected_options = input("Enter your choices (comma-separated): ").split(',')
        
        # Collect ignores from selections
        self.ignored_files = []
        for option in selected_options:
            option = option.strip()
            if option in predefined_ignores:
                self.ignored_files.extend(predefined_ignores[option])
            elif option == '6':
                # Manual entry
                manual_ignores = input("Enter custom ignores (comma-separated): ").split(',')
                self.ignored_files.extend([i.strip() for i in manual_ignores if i.strip()])

        # Write .gitignore if any files are selected
        if self.ignored_files:
            try:
                with open('.gitignore', 'w') as gitignore_file:
                    for entry in set(self.ignored_files):  # Remove duplicates
                        gitignore_file.write(f"{entry}\n")
                print("✅ .gitignore file created successfully!")
                print("Ignored files:", ", ".join(set(self.ignored_files)))
            except IOError as error:
                print(f"❌ .gitignore creation error: {error}")

    def stage_and_commit_changes(self):
        """
        Stage all changes and commit with a user-provided message.
        """
        self.git_config['commit_message'] = input("Enter commit message: ")
        
        staging_result = self.run_shell_command("git add .")
        commit_result = self.run_shell_command(
            f'git commit -m "{self.git_config["commit_message"]}"'
        )
        
        if staging_result and commit_result:
            print("✅ Changes staged and committed!")
        else:
            print("❌ Staging or commit failed.")

    def initialize_local_repository(self):
        """
        Initialize a new Git repository in the current directory.
        """
        if self.run_shell_command("git init"):
            print("✅ Local Git repository initialized!")
        else:
            print("❌ Repository initialization failed.")

    def link_remote_repository(self):
        """
        Link local repository to a remote GitHub repository with validation.
        """
        while True:
            repo_url = input("Enter full GitHub Repository URL (e.g., https://github.com/username/repo.git): ").strip()
            
            # Basic URL validation
            if repo_url.startswith(('https://github.com/', 'git@github.com:')) and repo_url.endswith('.git'):
                self.git_config['repository_url'] = repo_url
                
                if self.run_shell_command(f'git remote add origin {repo_url}'):
                    print("✅ Remote repository linked successfully!")
                    return
                else:
                    print("❌ Failed to link repository. Check URL and Git configuration.")
            else:
                print("❌ Invalid GitHub repository URL. Please provide a valid URL.")
                retry = input("Try again? (y/n): ").lower()
                if retry != 'y':
                    break

    def push_to_github(self):
        """
        Push local repository to GitHub.
        """
        branch_rename_result = self.run_shell_command("git branch -M main")
        push_result = self.run_shell_command("git push -u origin main")
        
        if branch_rename_result and push_result:
            print("✅ Code pushed to GitHub!")
        else:
            print("❌ GitHub push failed.")

    def display_github_creation_guide(self):
        """
        Provide guidance for creating a GitHub repository.
        """
        print("\n--- GitHub Repository Creation Guide ---")
        print("1. Visit https://github.com/new")
        print("2. Create an empty repository")
        print("3. Do NOT add README, .gitignore, or LICENSE")
        input("Press Enter after creating the repository...")

    def run_interactive_setup(self):
        """
        Interactive menu-driven Git and GitHub setup.
        """
        # First, select project directory
        if not self.select_project_directory():
            print("Project directory selection failed. Exiting.")
            return

        menu_options: Dict[str, Callable] = {
            '1': self.configure_git_credentials,
            '2': self.initialize_local_repository,
            '3': self.create_comprehensive_gitignore,
            '4': self.stage_and_commit_changes,
            '5': self.link_remote_repository,
            '6': self.push_to_github
        }

        while True:
            print("\n--- Git & GitHub Setup Wizard ---")
            print("\n".join([
                f"Current Directory: {self.project_directory}",
                "1. Configure Git Credentials",
                "2. Initialize Local Repository",
                "3. Create .gitignore",
                "4. Stage and Commit Changes",
                "5. Link Remote Repository",
                "6. Push to GitHub",
                "7. Exit"
            ]))

            choice = input("Select an option (1-7): ")
            
            if choice == '7':
                print("Exiting Git Setup Wizard...")
                break
            
            selected_action = menu_options.get(choice)
            if selected_action:
                selected_action()
            else:
                print("❌ Invalid option. Try again.")

def main():
    """
    Main entry point for the Git and GitHub setup script.
    """
    git_setup_wizard = GitHubSetup()
    git_setup_wizard.run_interactive_setup()

if __name__ == "__main__":
    main()