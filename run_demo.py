"""Run three releases and watch long-term memory decide NEW / CHANGED / UNCHANGED / REMOVED."""
import step1_memory_store as memory
from step4_agent import process_release, reviewer_edit

memory.reset()   # start with an empty memory

# Release 1: memory is empty, so everything is NEW
process_release("Release 1", [
    {"module": "Payments", "title": "Transfer limit",
     "text": "Customer can transfer up to 10,000 per transaction."},
    {"module": "Payments", "title": "Beneficiary nickname",
     "text": "Customer can set a nickname for a beneficiary."},
])

# A reviewer improves one test case in JIRA
reviewer_edit("TC-REQ-PAY-002-01", "Beneficiary nickname: saved and shown in the payee list", "Priya")

# Release 2: title reworded + limit changed, nickname only reworded, OTP is new
process_release("Release 2", [
    {"module": "Payments", "title": "Transfer limits",                     # plural title
     "text": "Customers can transfer up to 15,000 per transaction."},      # 10,000 -> 15,000
    {"module": "Payments", "title": "Beneficiary nickname",
     "text": "Customers can set a nickname for a beneficiary."},           # wording drift only
    {"module": "Payments", "title": "OTP challenge",
     "text": "Transfers above 5,000 require an OTP."},                     # brand new
])

# Release 3: same as release 2, but the nickname feature was dropped
process_release("Release 3", [
    {"module": "Payments", "title": "Transfer limits",
     "text": "Customers can transfer up to 15,000 per transaction."},
    {"module": "Payments", "title": "OTP challenge",
     "text": "Transfers above 5,000 require an OTP."},
])

print(f"\nMemory files: {memory.STATE_FILE} and {memory.AUDIT_FILE}")
