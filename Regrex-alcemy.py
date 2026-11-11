Work Item: Testing LLM-Based Layout Correction for Ground Truth Generation
Approach: Tested the script to correct Heron-generated layouts using Gemma 4 12B and Qwen Flash Next. Gemma did not produce the expected results, while Qwen Flash Next performed well. Analysed the output to identify issues in layout labels and bounding boxes.
2. Work Item: Improving Layout Correction Approach
Approach: Discussed the issues with Sorna N.A. and identified that assigning multiple tasks to the LLM at once affected the results. Split the process into three separate tasks: label correction, bounding box correction, and adding missing bounding boxes. Planned to validate the updated script and check the results today.
