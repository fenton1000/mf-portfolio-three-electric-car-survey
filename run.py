import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('electric_car_survey')


def welcome_page_choices():
    """
    Writes the welcome message and presents the user's opening options.
    Returns the chosen option.
    """
    print('Welcome to the Electric Car Survey!\n')
    print('Please select from the following options:\n')
    print('1. Complete the Survey\n')
    print('2. View Summary of Survey Analysis\n')
    choice = input('Please enter the number for your chosen option here:\n')

    return choice


def run_survey():
    """
    Runs the survey part of the application.
    Asks each of the questions contained in the questions worksheet in
    turn by calling the get question function and printing the returned
    question to screen.
    Returns the users responses to all questions as a list.
    """
    number_of_questions = get_number_of_questions()
    survey_welcome_choices(number_of_questions)
    ind = 1
    responses = []

    while ind <= number_of_questions:
        question = get_question(ind)
        display_question_format = question[1].split('#')
        last_index = len(display_question_format) - 1
        part = 0

        print(f'\nQuestion {ind}:')

        while part <= last_index:
            print(display_question_format[part])
            part += 1
        
        print(' \n')
        ind += 1
        final_answer_index = len(question) - 1
        answer_index = 2

        while answer_index <= final_answer_index:
            answer_number = answer_index - 1
            print(f'Answer {answer_number}: {question[answer_index]}\n')
            answer_index += 1

        response = input('Please enter the number for your answer:\n')
        responses.append(response)

    return responses


def get_number_of_questions():
    """
    Gets the number of questions in the current version of the survey.
    """
    questions_worksheet = SHEET.worksheet('questions')
    number_of_questions = len(questions_worksheet.row_values(1))

    return number_of_questions


def survey_welcome_choices(num):
    """
    Writes the welcome message for the survey option
    and presents the user with options to continue or exit.
    """
    print('\n You have chosen option 1 Complete the Survey!\n')
    print('Thank you for opting to take part in this survey.')
    print("We hope to gain insight into people's current")
    print('attitudes towards electric cars.')
    print(f'The survey consists of {num} questions')
    print('with multiple choice answers.')
    print('For each question please enter the number')
    print('of the one answer that best reflects your view.\n')
    print('Do you wish to continue?')
    choice = input('Please enter Y for Yes or N for No here: Y/N\n')

    if choice == 'N':
        print('Thank you for your interest!')
        print('You have exited the program!')
        raise SystemExit()


def get_question(ind):
    """
    Imports the required survey question from the questions worksheet
    """
    questions_worksheet = SHEET.worksheet('questions')
    question = questions_worksheet.col_values(ind)

    return question


def save_responses(responses):
    """
    Takes the responses from a particular survey, when passed to it,
    and saves them to the responses worksheet.
    """
    print('Saving responses...')
    responses_worksheet = SHEET.worksheet('responses')
    responses_worksheet.append_row(responses)


def analyze_data():
    """
    Calculates the percentage of respondants chosing each potential
    answer for each question.
    """
    print('Analyzing data...')
    number_of_questions = get_number_of_questions()
    questions_worksheet = SHEET.worksheet('questions')
    responses_worksheet = SHEET.worksheet('responses')
    question_num = 1

    while question_num <= number_of_questions:
        question_responses_col = responses_worksheet.col_values(question_num)
        question_responses = question_responses_col[1:]
        int_responses = [int(value) for value in question_responses]
        number_of_answers = len(questions_worksheet.col_values(question_num)) - 2

        percentages = []
        answer = 1
        while answer <= number_of_answers:
            is_a_match = 0
            for value in int_responses:
                if value == answer:
                    is_a_match += 1
            percentage = round((is_a_match/len(int_responses)) * 100, 1)
            percentages.append(percentage)
            answer += 1

        total = sum(percentages)
        roundby = round(100 - total, 1)
        indmax = percentages.index(max(percentages))
        replacement_val = round(percentages[indmax] + roundby, 1)
        percentages[indmax] = replacement_val
        add_data_to_stats_worksheet(percentages, question_num)

        question_num += 1
    
    print('Analysis complete! Thank you!')


def add_data_to_stats_worksheet(data, col):
    """
    Adds data provided in a list to the specified column
    overwriting the previous entry.
    """
    stats_worksheet = SHEET.worksheet('stats')
    row = 2
    last_entry_row = len(data) + 1
    ind = 0
    
    while row <= last_entry_row:
        stats_worksheet.update_cell(row, col, data[ind])
        row += 1
        ind += 1


def print_survey_analysis():
    """
    Prints the most recent survey analysis to screen
    """
    print('Retrieving survey analysis....\n')
    number_of_questions = get_number_of_questions()
    print('When asked the following questions:\n')
    ind = 1
    while ind <= number_of_questions:
        question = get_question(ind)
        stats = get_stats(ind)
        display_question_format = question[1].split('#')
        last_index = len(display_question_format) - 1
        part = 0
        print(f'Question {ind}:')
        while part <= last_index:
            print(display_question_format[part])
            part += 1
        
        print(' \n')
        ind += 1

        final_answer_index = len(question) - 1
        answer_index = 2
        stats_index = 0

        while answer_index <= final_answer_index:
            answer_number = answer_index - 1
            print(f'{stats[stats_index]}% of people replied:')
            print(f'Answer {answer_number}: {question[answer_index]}\n')
            answer_index += 1
            stats_index += 1


def get_stats(ind):
    """
    Imports the required survey stats from the stats worksheet
    """
    stats_worksheet = SHEET.worksheet('stats')
    stats = stats_worksheet.col_values(ind)[1:]

    return stats


def main():
    """
    Runs the application
    """
    choice = welcome_page_choices()
    if choice == '1':
        responses = run_survey()
        save_responses(responses)
        analyze_data()
    else:
        print_survey_analysis()


main()
