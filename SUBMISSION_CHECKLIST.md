# Submission checklist

1. Replace placeholder `Student Name` and `student@example.edu` in:
   - `paper/searchlens_report.tex`
   - `paper/searchlens_report.pdf` if you regenerate it
   - `slides/searchlens_presentation.pptx`
2. Run the verification commands:
   ```bash
   PYTHONPATH=src python scripts/run_experiments.py
   PYTHONPATH=src python -m unittest discover -s tests -v
   ```
3. Upload the full repository to the GitHub Classroom assignment.
4. Submit or present:
   - `paper/searchlens_report.pdf`
   - `slides/searchlens_presentation.pptx`
   - GitHub repository link
   - Optional deployed web demo link
5. For the bonus, deploy using the included `Dockerfile`, then put the public URL on the "Target Venue and Demo" slide.
