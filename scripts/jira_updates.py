from jira import JIRA

# Connect to Jira server
options = {"server": "https://your-jira-server.com"}
jira = JIRA(options, basic_auth=('your_username', 'your_password'))

def transition_issue(issue_key, transition_name):
    issue = jira.issue(issue_key)
    transitions = jira.transitions(issue)
    for transition in transitions:
        if transition['name'].lower() == transition_name.lower():
            jira.transition_issue(issue, transition['id'])
            print(f"Issue {issue_key} transitioned to {transition_name}.")
            return
    print(f"Transition {transition_name} not found for issue {issue_key}.")

def close_issue(issue_key, resolution_name, comment=None):
    issue = jira.issue(issue_key)
    transition_issue(issue_key, 'Done')
    jira.update_issue_field(issue_key, {"resolution": {"name": resolution_name}})
    if comment:
        jira.add_comment(issue, comment)
    print(f"Issue {issue_key} closed with resolution {resolution_name}.")

def create_subtasks(parent_issue_key, subtasks_info):
    created_subtasks = []
    for subtask in subtasks_info:
        subtask_data = {
            'project': {'key': jira.issue(parent_issue_key).fields.project.key},
            'parent': {'key': parent_issue_key},
            'summary': subtask['summary'],
            'description': subtask.get('description', ''),
            'issuetype': {'name': 'Sub-task'},
            'assignee': {'name': subtask.get('assignee')}
        }
        created_subtasks.append(jira.create_issue(fields=subtask_data))
        print(f"Subtask '{subtask['summary']}' created with key {created_subtasks[-1].key}.")
    return created_subtasks

def update_subtask(subtask_key, transition_name, resolution_name=None, comment=None):
    transition_issue(subtask_key, transition_name)
    if resolution_name:
        jira.update_issue_field(subtask_key, {"resolution": {"name": resolution_name}})
    if comment:
        jira.add_comment(subtask_key, comment)
    print(f"Subtask {subtask_key} updated to {transition_name} with resolution {resolution_name}.")

def check_and_close_parent_issue(parent_issue_key):
    parent_issue = jira.issue(parent_issue_key)
    subtasks = parent_issue.fields.subtasks
    all_completed = all(jira.issue(subtask.key).fields.status.name.lower() == 'done' for subtask in subtasks)
    
    if all_completed:
        close_issue(parent_issue_key, "Complete")
        print(f"Parent issue {parent_issue_key} closed as all subtasks are completed.")
    else:
        print(f"Parent issue {parent_issue_key} not closed as not all subtasks are completed.")

# Example usage:
issue_key = 'PROJECT-123'

# 1. Transition the issue to "In Progress"
transition_issue(issue_key, 'In Progress')

# 2. Create multiple subtasks
subtasks_info = [
    {'summary': 'Review code', 'description': 'Review the code for the new feature', 'assignee': 'user1'},
    {'summary': 'Write documentation', 'description': 'Document the feature', 'assignee': 'user2'},
    {'summary': 'Perform testing', 'description': 'Test the new feature', 'assignee': 'user3'}
]
subtasks = create_subtasks(issue_key, subtasks_info)

# 3. Comment on a subtask
jira.add_comment(subtasks[0].key, 'Please start the review process.')

# 4. Update subtask to "In Progress"
update_subtask(subtasks[0].key, 'In Progress')

# 5. Close subtask with resolution "Complete"
update_subtask(subtasks[0].key, 'Done', resolution_name='Complete', comment='Review completed successfully.')

# 6. Check if all subtasks are completed, and close the parent issue if they are
check_and_close_parent_issue(issue_key)
