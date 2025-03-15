import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import docx
import threading
import re
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image, ImageTk
import os

# Download necessary NLTK components
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9.,?\s]', '', text)  # Remove special characters
    return text.lower()


def find_answers(text, question):
    """Searches for relevant sentences from text that answer the given question."""
    sentences = sent_tokenize(text)
    question_words = set(word_tokenize(question.lower()))
    answers = []

    for sentence in sentences:
        words = set(word_tokenize(sentence.lower()))
        common_words = question_words.intersection(words)

        if len(common_words) > 2:  # Adjust threshold for better results
            answers.append(sentence)

    return answers


def plot_graph():
    """Plots a sample mathematical graph (e.g., y = x^2)."""
    x = sp.symbols('x')
    expr = x**2
    sp.plot(expr, title='Graph of y = x^2', show=True)


def display_equation():
    """Displays an equation in a new window."""
    eq_window = tk.Toplevel()
    eq_window.title("Mathematical Equation")
    equation = sp.Integral(sp.sin(sp.Symbol('x')), sp.Symbol('x'))
    eq_label = ttk.Label(eq_window, text=f"Equation: {equation.doit()}", font=('Arial', 12))
    eq_label.pack()


def display_image():
    """Displays a sample circuit image."""
    img_window = tk.Toplevel()
    img_window.title("Circuit Diagram")
    img_path = "circuit_diagram.jpg"  # Replace with actual image path
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img = img.resize((400, 300), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = ttk.Label(img_window, image=img)
        panel.image = img
        panel.pack()
    else:
        messagebox.showerror("Error", "Image not found!")


class AnswerAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Answer Generator with Math & Graphs")
        self.root.geometry("900x700")

        self.file_path = tk.StringVar()
        self.question_text = tk.StringVar()

        ttk.Label(root, text="Select Study Material:").pack()
        ttk.Entry(root, textvariable=self.file_path, width=60).pack()
        ttk.Button(root, text="Browse", command=self.browse_file).pack()

        ttk.Label(root, text="Enter Question:").pack()
        ttk.Entry(root, textvariable=self.question_text, width=60).pack()

        self.search_button = ttk.Button(root, text="Find Answer", command=self.find_answer)
        self.search_button.pack()

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        self.answer_text = scrolledtext.ScrolledText(root, width=100, height=20)
        self.answer_text.pack()

        ttk.Button(root, text="Save Answer", command=self.save_answer).pack()
        ttk.Button(root, text="Plot Graph", command=plot_graph).pack()
        ttk.Button(root, text="Show Equation", command=display_equation).pack()
        ttk.Button(root, text="Show Circuit", command=display_image).pack()

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[('PDF files', '*.pdf'), ('Word files', '*.docx')])
        if filename:
            self.file_path.set(filename)

    def find_answer(self):
        file_path = self.file_path.get()
        question = self.question_text.get()
        if not file_path or not question:
            messagebox.showerror("Error", "Please select a file and enter a question!")
            return

        self.answer_text.delete(1.0, tk.END)
        self.search_button.config(state=tk.DISABLED)
        self.progress_var.set(0)

        def process():
            try:
                self.progress_var.set(20)
                text = extract_text_from_pdf(file_path) if file_path.endswith('.pdf') else extract_text_from_docx(file_path)

                self.progress_var.set(50)
                text = clean_text(text)

                self.progress_var.set(80)
                answers = find_answers(text, question)

                if answers:
                    self.answer_text.insert(tk.END, "\n".join(answers))
                else:
                    self.answer_text.insert(tk.END, "No relevant answers found.")

                self.progress_var.set(100)
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.search_button.config(state=tk.NORMAL)
                self.progress_var.set(0)

        thread = threading.Thread(target=process)
        thread.start()

    def save_answer(self):
        answer = self.answer_text.get(1.0, tk.END).strip()
        if not answer:
            messagebox.showwarning("Warning", "No answer to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(answer)
            messagebox.showinfo("Success", "Answer saved successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnswerAssistant(root)
    root.mainloop()
