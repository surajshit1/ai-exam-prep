#!/usr/bin/env python3
"""
AI Exam Prep System - main.py
Entry point that gathers user input, validates it, and runs the ExamPrep crew.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project dir to path (if running from ai_exam_prep/)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from exam_prep.utils import validate_inputs, create_output_directory
from exam_prep.crew import ExamPrepCrew

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)


def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                    📘 AI EXAM PREP SYSTEM 📘                ║
    ║     Previous-year analysis · Topic explainer · Mock tests   ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_user_inputs():
    """Collect user inputs specific to exam prep."""
    try:
        print("\n📝 Please provide exam preparation details:\n")
        exam_type = input("📚 Exam type (e.g., SSC, UPSC, IELTS): ").strip()
        subjects = input("📖 Subjects/topics (comma-separated): ").strip()
        days_until_exam = int(input("⏳ Days until exam: ").strip())
        study_hours = int(input("⏰ Preferred study hours per day (1-24): ").strip())
        level = input("🎯 Current level (Beginner/Intermediate/Advanced): ").strip() or "Intermediate"
        pyq_folder = input("📁 Folder path containing previous year questions (pdf/txt/json). Leave blank if none: ").strip() or None

        validated = validate_inputs(
            exam_type=exam_type,
            subjects=subjects,
            days_until_exam=days_until_exam,
            study_hours=study_hours,
            level=level,
            pyq_folder=pyq_folder,
        )

        # Show summary and confirm
        print("\n" + "=" * 60)
        print("📋 INPUT SUMMARY:")
        print(f"   📚 Exam Type: {validated['exam_type']}")
        print(f"   📖 Subjects: {', '.join(validated['subjects'])}")
        print(f"   ⏳ Days until exam: {validated['days_until_exam']}")
        print(f"   ⏰ Study hours/day: {validated['study_hours']}")
        print(f"   🎯 Level: {validated['level']}")
        print(f"   🗂 PYQ folder: {validated.get('pyq_folder', 'None')}")
        print(f"   📆 Exam Date: {validated['exam_date_readable']}")
        print("=" * 60)

        confirm = input("\n✅ Is this information correct? (y/n): ").lower().strip()
        if confirm != "y":
            print("❌ Please restart and enter the correct information.")
            return None

        return validated

    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return None
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user.")
        return None


def main():
    print_banner()

    # Prepare environment check (Gemini key used by crew)
    gemini_key = os.getenv("GEMINI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")

    if not gemini_key:
        print("❌ Missing GEMINI_API_KEY in .env. Please add it and retry.")
        return
    if not serper_key:
        print("❌ Missing SERPER_API_KEY in .env. Please add it and retry.")
        return

    inputs = get_user_inputs()
    if not inputs:
        return

    # Ensure output dir
    create_output_directory()

    try:
        print("\n🤖 Initializing ExamPrep crew and agents...")
        crew = ExamPrepCrew()
        print("📊 Running exam preparation pipeline...")

        # kickoff returns whatever the crew returns; Crew will produce files in output/
        result = crew.crew().kickoff(inputs=inputs)

        print("\n🎉 Exam Prep completed. Check the 'output/' folder for reports:")
        print("   01_pyq_analysis.md       - PYQ analysis and topic frequency")
        print("   02_topic_explanations.md - Topic explanations & examples")
        print("   03_mock_test.md         - Generated mock test (questions + answers)")
        print("   04_weakness_report.md   - Weakness diagnostics from mock test")
        print("   05_study_plan.md        - Personalized study plan")
    except Exception as e:
        print(f"❌ Error running ExamPrep crew: {e}")


if __name__ == "__main__":
    main()
