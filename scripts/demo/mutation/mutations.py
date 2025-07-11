"""
Mutation configurations for the mutation testing demo.

This module contains the mutation specifications that can be applied
to different repositories during mutation testing.
"""

# Mutation configurations for different repositories
# Each repository can have multiple mutations
MUTATIONS = {
    "demo-httpie-cli": [
        {
            "id": "none_check_logic",
            "file_path": "httpie/cli/dicts.py",
            "line_number": 26,
            "find_pattern": r"if value is None:",
            "replace_pattern": "if value is not None:",
            "description": "Change None check logic"
        }
    ],
    "demo-pallets-click": [
        {
            "id": "encoding_assignment",
            "file_path": "src/click/utils.py",
            "line_number": 126,
            "find_pattern": r"self.encoding = encoding",
            "replace_pattern": "self.encoding = \"utf-16\"",
            "description": "Change encoding assignment"
        }
    ],
    "demo-psf-requests": [
        {
            "id": "status_code_description",
            "file_path": "src/requests/status_codes.py",
            "line_number": 87,
            "find_pattern": r'444: \("no_response", "none"\),',
            "replace_pattern": '444: ("no_response", "no"),',
            "description": "Change status code description"
        }
    ]
}

def get_mutation(repo_name, mutation_id=None):
    """
    Get mutation configuration for a repository.
    
    Args:
        repo_name: Name of the repository
        mutation_id: ID of the specific mutation (optional, defaults to first mutation)
        
    Returns:
        Mutation configuration dictionary
    """
    if repo_name not in MUTATIONS:
        return None
    
    mutations = MUTATIONS[repo_name]
    if not mutations:
        return None
    
    if mutation_id is None:
        return mutations[0]  # Return first mutation by default
    
    # Find mutation by ID
    for mutation in mutations:
        if mutation.get("id") == mutation_id:
            return mutation
    
    return None