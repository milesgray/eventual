## Core Workflow Patterns

### 1. Initialization Workflow

**Description**: Sets up memory structures and verifies context.

**Steps**:
1.  Create the necessary directories and files in the `.gemini/` directory if they don't exist.
2.  Load the existing context from the files.
3.  Activate the virtual environment using `source env/bin/activate`.

### 2. Documentation Workflow

**Description**: Creates and maintains comprehensive documentation.

**Steps**:
1.  Create a task log for each task.
2.  Update the relevant memory files (e.g., `activeContext.md`, `progress.md`).
3.  Commit the changes to git.

### 3. Implementation Workflow

**Description**: Executes tasks with quality standards enforcement.

**Steps**:
1.  Understand the task requirements.
2.  Develop a plan for implementing the task.
3.  Implement the task.
4.  Test the implementation.
5.  Document the implementation in the task log.

### 4. Error Recovery Workflow

**Description**: Detects and resolves failures systematically.

**Steps**:
1.  Detect the error.
2.  Document the error in the `errors/` directory.
3.  Identify the cause of the error.
4.  Develop a plan for resolving the error.
5.  Implement the plan.
6.  Test the solution.
7.  Document the resolution in the error log.

### 5. Evaluation Workflow

**Description**: Measures performance against standards.

**Steps**:
1.  Define the evaluation criteria.
2.  Evaluate the performance of the task.
3.  Assign a score based on the performance standards.
4.  Identify strengths and areas for improvement.
5.  Document the evaluation in the task log.

### 6. Self-Critique Workflow

**Description**: Reviews and improves implementation.

**Steps**:
1.  Review the task log.
2.  Identify areas for improvement.
3.  Implement the improvements.
4.  Test the improvements.
5.  Document the improvements in the task log.
