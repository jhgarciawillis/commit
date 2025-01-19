import os
import subprocess
import sys
from typing import List, Dict, Optional

import streamlit as st
import extra_streamlit_components as stx

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
            st.success(result.stdout)
            return True
        except subprocess.CalledProcessError as error:
            st.error(f"Command Execution Error: {error}")
            st.error(error.stderr)
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
            st.success("Git is already installed.")
            return True
        except FileNotFoundError:
            st.warning("Git is not installed.")
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
        
        st.info("--- Git Installation Guide ---")
        for platform, link in installation_guides.items():
            st.write(f"{platform}: {link}")

    def select_project_directory(self) -> bool:
        """
        Allow user to select project directory in Streamlit.
        
        Returns:
            bool: True if a valid directory is selected, False otherwise
        """
        directory_input = st.text_input(
            "Enter full project directory path", 
            placeholder="e.g., C:\\Users\\luisg\\Downloads\\Code\\Piano"
        )
        
        if directory_input:
            directory_path = directory_input.strip()
            
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                try:
                    os.chdir(directory_path)
                    self.project_directory = directory_path
                    st.success(f"Project directory set to: {self.project_directory}")
                    return True
                except Exception as e:
                    st.error(f"Error changing directory: {e}")
            else:
                st.error("Invalid directory. Please check the path and try again.")
        
        return False

    def check_existing_git_config(self) -> Optional[dict]:
        """
        Check existing Git configuration.
        
        Returns:
            Optional[dict]: Existing Git configuration or None
        """
        try:
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
            
            if username_cmd.returncode == 0 and email_cmd.returncode == 0:
                existing_config = {
                    'username': username_cmd.stdout.strip(),
                    'email': email_cmd.stdout.strip()
                }
                return existing_config
            return None
        except Exception as e:
            st.error(f"Error checking Git configuration: {e}")
            return None

    def configure_git_credentials(self):
        """
        Configure Git credentials in Streamlit interface.
        """
        st.header("Git Credentials Configuration")
        
        existing_config = self.check_existing_git_config()
        
        if existing_config:
            st.info(f"Current Username: {existing_config['username']}")
            st.info(f"Current Email: {existing_config['email']}")
            
            config_choice = st.radio(
                "Git Configuration", 
                ["Keep Existing", "Update Credentials", "Cancel"]
            )
            
            if config_choice == "Keep Existing":
                self.git_config['username'] = existing_config['username']
                self.git_config['email'] = existing_config['email']
                st.success("Existing Git configuration retained.")
                return
            elif config_choice == "Cancel":
                st.warning("Git configuration setup cancelled.")
                return
        
        # New configuration inputs
        new_username = st.text_input("Enter Git Username")
        new_email = st.text_input("Enter Git Email")
        
        if st.button("Configure Git Credentials"):
            if new_username and new_email:
                username_cmd = f'git config --global user.name "{new_username}"'
                email_cmd = f'git config --global user.email "{new_email}"'
                
                if (self.run_shell_command(username_cmd) and 
                    self.run_shell_command(email_cmd)):
                    st.success("Git credentials configured successfully!")
                else:
                    st.error("Configuration failed.")
            else:
                st.error("Please provide both username and email.")

    def create_comprehensive_gitignore(self):
        """
        Create a comprehensive .gitignore with Streamlit interface.
        """
        st.header(".gitignore Configuration")
        
        predefined_ignores = {
            'Node.js': ['node_modules/', '*.log', '.DS_Store'],
            'Python': ['*.pyc', '__pycache__/', '.venv/', 'venv/'],
            'Java': ['*.class', 'target/', 'build/'],
            'IDE': ['.idea/', '.vscode/', '*.sublime-project'],
            'Temp Files': ['*.swp', '*.swo', '*~']
        }

        selected_templates = st.multiselect(
            "Select predefined .gitignore templates",
            list(predefined_ignores.keys())
        )

        custom_ignores = st.text_area(
            "Add custom ignore patterns (comma-separated)",
            placeholder="e.g., *.log, build/, secrets.json"
        )

        if st.button("Create .gitignore"):
            self.ignored_files = []
            
            # Add selected templates
            for template in selected_templates:
                self.ignored_files.extend(predefined_ignores[template])
            
            # Add custom ignores
            if custom_ignores:
                custom_list = [i.strip() for i in custom_ignores.split(',') if i.strip()]
                self.ignored_files.extend(custom_list)

            try:
                with open('.gitignore', 'w') as gitignore_file:
                    for entry in set(self.ignored_files):
                        gitignore_file.write(f"{entry}\n")
                st.success("✅ .gitignore file created successfully!")
                st.write("Ignored files:", ", ".join(set(self.ignored_files)))
            except IOError as error:
                st.error(f"❌ .gitignore creation error: {error}")

    def stage_and_commit_changes(self):
        """
        Stage and commit changes via Streamlit.
        """
        st.header("Stage and Commit Changes")
        
        commit_message = st.text_input("Enter commit message")
        
        if st.button("Stage and Commit"):
            if commit_message:
                staging_result = self.run_shell_command("git add .")
                commit_result = self.run_shell_command(
                    f'git commit -m "{commit_message}"'
                )
                
                if staging_result and commit_result:
                    st.success("✅ Changes staged and committed!")
                else:
                    st.error("❌ Staging or commit failed.")
            else:
                st.error("Please provide a commit message.")

    def initialize_local_repository(self):
        """
        Initialize a new Git repository via Streamlit.
        """
        st.header("Initialize Local Repository")
        
        if st.button("Initialize Git Repository"):
            if self.run_shell_command("git init"):
                st.success("✅ Local Git repository initialized!")
            else:
                st.error("❌ Repository initialization failed.")

    def link_remote_repository(self):
        """
        Link local repository to remote GitHub repository.
        """
        st.header("Link Remote Repository")
        
        repo_url = st.text_input(
            "Enter full GitHub Repository URL", 
            placeholder="https://github.com/username/repo.git"
        )
        
        if st.button("Link Remote Repository"):
            if repo_url.startswith(('https://github.com/', 'git@github.com:')) and repo_url.endswith('.git'):
                self.git_config['repository_url'] = repo_url
                
                if self.run_shell_command(f'git remote add origin {repo_url}'):
                    st.success("✅ Remote repository linked successfully!")
                else:
                    st.error("❌ Failed to link repository. Check URL and Git configuration.")
            else:
                st.error("❌ Invalid GitHub repository URL.")

    def push_to_github(self):
        """
        Push local repository to GitHub via Streamlit.
        """
        st.header("Push to GitHub")
        
        if st.button("Push to GitHub"):
            branch_rename_result = self.run_shell_command("git branch -M main")
            push_result = self.run_shell_command("git push -u origin main")
            
            if branch_rename_result and push_result:
                st.success("✅ Code pushed to GitHub!")
            else:
                st.error("❌ GitHub push failed.")

def main():
    """
    Streamlit app main function.
    """
    st.title("🚀 Git & GitHub Setup Wizard")
    
    # Initialize GitHubSetup
    git_setup_wizard = GitHubSetup()
    
    # Sidebar navigation
    menu_options = [
        "Project Directory",
        "Git Credentials",
        "Initialize Repository",
        "Create .gitignore",
        "Stage & Commit",
        "Link Remote Repository",
        "Push to GitHub"
    ]
    
    choice = st.sidebar.radio("Navigation", menu_options)
    
    # Function mapping
    if choice == "Project Directory":
        git_setup_wizard.select_project_directory()
    elif choice == "Git Credentials":
        git_setup_wizard.configure_git_credentials()
    elif choice == "Initialize Repository":
        git_setup_wizard.initialize_local_repository()
    elif choice == "Create .gitignore":
        git_setup_wizard.create_comprehensive_gitignore()
    elif choice == "Stage & Commit":
        git_setup_wizard.stage_and_commit_changes()
    elif choice == "Link Remote Repository":
        git_setup_wizard.link_remote_repository()
    elif choice == "Push to GitHub":
        git_setup_wizard.push_to_github()

if __name__ == "__main__":
    main()
