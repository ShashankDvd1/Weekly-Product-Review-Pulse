import sys

# 1. Update orchestrator.py
with open('backend/agents/orchestrator.py', 'r', encoding='utf-8') as f:
    orch = f.read()

orch = orch.replace(
    'Hypothesis, InterviewQuestion, ExecutiveSummary,',
    'Hypothesis, OptimizedInterviewQuestion, InterviewScriptOutput, ExecutiveSummary,'
)
orch = orch.replace(
    'self.interview_questions: list[InterviewQuestion] = []',
    'self.interview_script = None'
)
orch = orch.replace(
    '''        self.interview_questions = generate_interview_questions(
            self.personas, self.barriers, self.hypotheses
        )
        self._log_progress(f"  ✅ {len(self.interview_questions)} interview questions generated")''',
    '''        self.interview_script = generate_interview_questions(
            self.personas, self.barriers, self.hypotheses
        )
        self._log_progress(f"  ✅ {len(self.interview_script.optimized_script) if self.interview_script else 0} optimized questions generated")'''
)
orch = orch.replace(
    '"interview_questions": [q.model_dump() for q in self.interview_questions],',
    '"interview_script": self.interview_script.model_dump() if self.interview_script else None,'
)

with open('backend/agents/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(orch)

# 2. Update main.py
with open('backend/main.py', 'r', encoding='utf-8') as f:
    main = f.read()

main = main.replace(
    '''    return {
        "status": "success",
        "questions": [q.model_dump() for q in orchestrator.interview_questions],
        "count": len(orchestrator.interview_questions),
    }''',
    '''    return {
        "status": "success",
        "script": orchestrator.interview_script.model_dump() if orchestrator.interview_script else None
    }'''
)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(main)

# 3. Update mcp_server.py
with open('backend/mcp_server.py', 'r', encoding='utf-8') as f:
    mcp = f.read()

mcp = mcp.replace(
    '''        orchestrator.interview_questions = generate_interview_questions(
            orchestrator.personas, orchestrator.barriers, orchestrator.hypotheses
        )
        return {"questions": [q.model_dump() for q in orchestrator.interview_questions]}''',
    '''        orchestrator.interview_script = generate_interview_questions(
            orchestrator.personas, orchestrator.barriers, orchestrator.hypotheses
        )
        return {"script": orchestrator.interview_script.model_dump() if orchestrator.interview_script else None}'''
)

with open('backend/mcp_server.py', 'w', encoding='utf-8') as f:
    f.write(mcp)

print('Updated successfully')
