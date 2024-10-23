import json

def load_grades(filename):
    """Load grades from a JSON file."""
    try:
        with open(filename, 'r') as f:
            grades = json.load(f)
            return grades
    except FileNotFoundError:
        print("Grades file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return {}

def calculate_average(grades):
    """Calculate the average of the grades."""
    if not grades:
        return 0
    return sum(grades) / len(grades)

def main():
    # Load grades from a file
    grades_file = 'grades.json'  # Change this to your actual grades file path
    grades = load_grades(grades_file)

    # Calculate average grade
    average = calculate_average(grades)
    
    # Print results
    if grades:
        print(f"Grades: {grades}")
        print(f"Average Grade: {average:.2f}")
    else:
        print("No grades to display.")

if __name__ == "__main__":
    main()
