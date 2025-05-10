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
1.  Create a task log for each task. Task log filenames should include a unique identifier (e.g., timestamp or UUID) to avoid collisions.
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

**Description**: Reviews and improves implementation based on evaluation results through structured iteration.

**Steps**:
1.  Review the task log and the performance evaluation.
2.  Perform Gap Analysis: Identify specific areas where performance fell short of standards or where improvements are needed.
3.  Develop an Iterative Optimization Plan: Outline concrete steps to address the identified gaps and improve the implementation.
4.  Implement the improvements.
5.  Test the improvements.
6.  Document the improvements and re-evaluate performance in the task log.

## Structured Decision Optimization Principles

The Evaluation and Self-Critique Workflows drive Structured Decision Optimization, which follows these principles:

1.  **Objective Measurement**: Every decision and implementation is evaluated against quantifiable criteria (Performance Standards).
2.  **Gap Analysis**: Performance shortfalls and areas for improvement are systematically identified based on evaluation results.
3.  **Iterative Optimization**: Solutions are refined through a structured iterative process until they meet or exceed target scores or requirements.
4.  **Pattern Recognition**: Successful approaches, solutions, and optimization strategies are identified and documented for future application.
5.  **Knowledge Persistence**: All evaluations, identified gaps, optimization plans, and outcomes are stored in the Memory Bank to ensure continuous learning and improvement.
