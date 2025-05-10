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

**Description**: Measures performance against standards and identifies areas for optimization based on quantifiable criteria.

**Steps**:
1.  Define the evaluation criteria based on task goals and performance standards.
2.  Evaluate the performance of the task against the defined criteria.
3.  Assign a numerical score based on the performance standards.
4.  Perform a gap analysis to identify discrepancies between expected and actual performance.
5.  Document the evaluation, score, and identified gaps in the task log.

### 6. Self-Critique Workflow

**Description**: Reviews evaluations, identifies root causes of performance gaps, and devises iterative improvements based on structured analysis.

**Steps**:
1.  Review the task log, focusing on the evaluation and identified gaps.
2.  Analyze the root causes of performance shortfalls using a structured approach (e.g., 5 Whys, fault tree analysis - although these are advanced and not strictly implemented here, the *principle* of root cause analysis is applied).
3.  Develop a plan for iterative optimization, focusing on addressing the root causes of the most significant performance gaps.
4.  Implement the planned improvements.
5.  Test the improvements to verify their effectiveness.
6.  Document the self-critique process, including root cause analysis, improvement plan, and test results, in the task log.

## Structured Decision Optimization Principles (Applied in Evaluation and Self-Critique)

1.  **Objective Measurement**: Every decision is evaluated against quantifiable criteria (Performance Standards).
2.  **Gap Analysis**: Performance shortfalls are systematically identified and addressed (Evaluation Workflow Step 4).
3.  **Iterative Optimization**: Solutions are refined until they meet or exceed target scores (Self-Critique Workflow Steps 3-5).
4.  **Pattern Recognition**: Successful approaches are documented for future application (Implicit in comprehensive task logs and updated memory files).
5.  **Knowledge Persistence**: All evaluations and optimizations are stored in the Memory Bank (Documentation Workflow).

This process ensures decisions are made based on evidence rather than intuition and solutions continuously improve through structured iteration.
