import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from typing import List, Dict, Any

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Quiz Application")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Quiz data
        self.questions = self.load_questions()
        self.current_question = 0
        self.score = 0
        self.total_questions = len(self.questions)
        
        # Variables
        self.selected_answer = tk.StringVar()
        self.time_left = tk.IntVar()
        self.timer_running = False
        
        self.setup_ui()
        self.start_quiz()
    
    def load_questions(self) -> List[Dict[str, Any]]:
        """Load quiz questions from JSON file"""
        try:
            with open('questions.json', 'r') as f:
                questions = json.load(f)
                print(f"✅ Loaded {len(questions)} questions from questions.json")
                return questions
        except FileNotFoundError:
            print("❌ Error: questions.json not found!")
            print("Please make sure questions.json exists in the same folder.")
            return []
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON format in questions.json!")
            return []
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Interactive Quiz", 
            font=("Arial", 24, "bold"),
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Progress and timer frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=self.total_questions,
            length=400
        )
        self.progress_bar.grid(row=0, column=0, padx=(0, 20))
        
        # Timer
        self.timer_label = ttk.Label(
            progress_frame, 
            text="Time: 30s",
            font=("Arial", 12),
            foreground="#e74c3c"
        )
        self.timer_label.grid(row=0, column=1)
        
        # Question frame
        self.question_frame = ttk.Frame(main_frame)
        self.question_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Question label
        self.question_label = ttk.Label(
            self.question_frame,
            text="",
            font=("Arial", 14),
            wraplength=600,
            justify="center"
        )
        self.question_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Options frame
        self.options_frame = ttk.Frame(self.question_frame)
        self.options_frame.grid(row=1, column=0, columnspan=2)
        
        # Answer buttons
        self.answer_buttons = []
        for i in range(4):
            btn = ttk.Button(
                self.options_frame,
                text="",
                command=lambda x=i: self.select_answer(x),
                style="Answer.TButton"
            )
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E), padx=(0, 10))
            self.answer_buttons.append(btn)
        
        # Submit button
        self.submit_button = ttk.Button(
            main_frame,
            text="Submit Answer",
            command=self.submit_answer,
            style="Submit.TButton"
        )
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Score label
        self.score_label = ttk.Label(
            main_frame,
            text="Score: 0/0",
            font=("Arial", 12, "bold"),
            foreground="#27ae60"
        )
        self.score_label.grid(row=4, column=0, columnspan=2)
        
        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        self.prev_button = ttk.Button(
            nav_frame,
            text="Previous",
            command=self.previous_question,
            state="disabled"
        )
        self.prev_button.grid(row=0, column=0, padx=(0, 10))
        
        self.next_button = ttk.Button(
            nav_frame,
            text="Next",
            command=self.next_question,
            state="disabled"
        )
        self.next_button.grid(row=0, column=1, padx=(0, 10))
        
        self.finish_button = ttk.Button(
            nav_frame,
            text="Finish Quiz",
            command=self.finish_quiz,
            state="disabled"
        )
        self.finish_button.grid(row=0, column=2)
        
        # Configure styles
        style = ttk.Style()
        style.configure("Answer.TButton", padding=10, font=("Arial", 11))
        style.configure("Submit.TButton", padding=15, font=("Arial", 12, "bold"))
    
    def start_quiz(self):
        """Start the quiz and display the first question"""
        self.current_question = 0
        self.score = 0
        self.display_question()
        self.start_timer()
    
    def display_question(self):
        """Display the current question and options"""
        if self.current_question < self.total_questions:
            question_data = self.questions[self.current_question]
            
            # Update question
            self.question_label.config(text=f"Question {self.current_question + 1}: {question_data['question']}")
            
            # Update options
            for i, option in enumerate(question_data['options']):
                self.answer_buttons[i].config(text=f"{chr(65 + i)}. {option}")
                self.answer_buttons[i].config(state="normal")
            
            # Reset selection
            self.selected_answer.set("")
            
            # Update progress
            self.progress_var.set(self.current_question + 1)
            
            # Update navigation buttons
            self.update_navigation_buttons()
            
            # Reset timer
            self.reset_timer()
        else:
            self.finish_quiz()
    
    def select_answer(self, answer_index):
        """Select an answer option"""
        self.selected_answer.set(str(answer_index))
        
        # Highlight selected button
        for i, btn in enumerate(self.answer_buttons):
            if i == answer_index:
                btn.config(style="Selected.TButton")
            else:
                btn.config(style="Answer.TButton")
    
    def submit_answer(self):
        """Submit the selected answer"""
        if not self.selected_answer.get():
            messagebox.showwarning("No Answer Selected", "Please select an answer before submitting.")
            return
        
        selected = int(self.selected_answer.get())
        correct = self.questions[self.current_question]['correct']
        
        # Check if answer is correct
        if selected == correct:
            self.score += 1
            messagebox.showinfo("Correct!", f"Great job! {self.questions[self.current_question]['explanation']}")
        else:
            correct_answer = self.questions[self.current_question]['options'][correct]
            messagebox.showinfo("Incorrect", 
                              f"Sorry, that's wrong. The correct answer is: {correct_answer}\n\n"
                              f"Explanation: {self.questions[self.current_question]['explanation']}")
        
        # Update score
        self.score_label.config(text=f"Score: {self.score}/{self.current_question + 1}")
        
        # Disable submit button
        self.submit_button.config(state="disabled")
        
        # Enable navigation buttons
        self.next_button.config(state="normal")
        if self.current_question == self.total_questions - 1:
            self.finish_button.config(state="normal")
    
    def next_question(self):
        """Move to the next question"""
        if self.current_question < self.total_questions - 1:
            self.current_question += 1
            self.display_question()
            self.submit_button.config(state="normal")
            self.next_button.config(state="disabled")
            self.finish_button.config(state="disabled")
    
    def previous_question(self):
        """Move to the previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            self.display_question()
            self.submit_button.config(state="normal")
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        self.prev_button.config(state="normal" if self.current_question > 0 else "disabled")
        self.next_button.config(state="disabled")
        self.finish_button.config(state="disabled")
    
    def start_timer(self):
        """Start the countdown timer"""
        self.time_left.set(30)
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update the timer display"""
        if self.timer_running and self.time_left.get() > 0:
            self.timer_label.config(text=f"Time: {self.time_left.get()}s")
            self.time_left.set(self.time_left.get() - 1)
            self.root.after(1000, self.update_timer)
        elif self.time_left.get() <= 0:
            self.timer_label.config(text="Time's up!")
            self.timer_running = False
            # Auto-submit if no answer selected
            if not self.selected_answer.get():
                messagebox.showinfo("Time's Up!", "Time ran out! Moving to next question.")
                self.next_question()
    
    def reset_timer(self):
        """Reset the timer for the current question"""
        self.timer_running = False
        self.start_timer()
    
    def finish_quiz(self):
        """Finish the quiz and show results"""
        self.timer_running = False
        
        # Calculate percentage
        percentage = (self.score / self.total_questions) * 100
        
        # Determine grade
        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "F"
        
        # Show results
        result_message = f"""Quiz Complete!

Final Score: {self.score}/{self.total_questions}
Percentage: {percentage:.1f}%
Grade: {grade}

"""
        
        if percentage >= 70:
            result_message += "🎉 Congratulations! You did great!"
        elif percentage >= 50:
            result_message += "👍 Good effort! Keep practicing!"
        else:
            result_message += "📚 Keep studying! You'll improve with practice!"
        
        messagebox.showinfo("Quiz Results", result_message)
        
        # Ask if user wants to retake
        if messagebox.askyesno("Retake Quiz", "Would you like to retake the quiz?"):
            self.start_quiz()
        else:
            self.root.quit()

def main():
    """Main function to run the quiz application"""
    root = tk.Tk()
    app = QuizApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"800x600+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
