"""
Module for Survey
"""
import gspread
from google.oauth2.service_account import Credentials
from colorama import Fore, Style

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('electric_car_survey')


def validate_input(value, allowed):
    """
    Runs the validation of data for inputs using the
    value of the input and a list of allowed inputs
    """
    for item in allowed:
        if value == item:
            return True

    print(Fore.RED + '\nInvalid Entry!! Enter value for given options only!!')
    return False


def welcome_page_choices():
    """
    Writes the welcome message and presents the user's opening options.
    Returns the chosen option.
    """
    print(Fore.GREEN + 'Welcome to the Electric Car Survey!\n')
    while True:
        print(Fore.BLUE + 'Please select from the following options:\n')
        print('1. Complete the Survey')
        print('2. View Summary of Survey Analysis\n')
        choice = input('Enter the number for your chosen option here:\n')
        choice_stripped = choice.strip()

        if validate_input(choice_stripped, ['1', '2']):
            break

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
    question_num = 1
    responses = []

    while question_num <= number_of_questions:
        question = get_question(question_num)
        display_question_format = question[1].split('#')
        last_index = len(display_question_format) - 1
        part = 0

        print(Fore.GREEN + f'\nQuestion {question_num}:')

        while part <= last_index:
            print(display_question_format[part])
            part += 1

        print(' \n')
        question_num += 1
        final_answer_index = len(question) - 1
        ans_ind = 2

        while ans_ind <= final_answer_index:
            ans_num = ans_ind - 1
            print(Fore.BLUE + f'Answer {ans_num}: {question[ans_ind]}\n')
            ans_ind += 1

        while True:
            response = input('Please enter the number for your answer:\n')
            response_stripped = response.strip()
            allowed_nums = range(1, ans_num + 1)
            allowed = [str(x) for x in allowed_nums]

            if validate_input(response_stripped, allowed):
                break

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
    print(Fore.GREEN + '\n You have chosen option 1 Complete the Survey!\n')
    print('Thank you for opting to take part in this survey.')
    print("We hope to gain insight into people's current")
    print('attitudes towards electric cars.')
    print(f'The survey consists of {num} questions')
    print('with multiple choice answers.')
    print('For each question please enter the number')
    print('of the one answer that best reflects your view.\n')
    print(Fore.BLUE + 'Do you wish to continue?')

    while True:
        choice = input(Fore.BLUE + 'Please enter Y for Yes or N for No Y/N:\n')
        choice_stripped = choice.strip()

        if validate_input(choice_stripped, ['Y', 'y', 'N', 'n']):
            break

    if choice_stripped.upper() == 'N':
        print(Fore.RED + 'Thank you for your interest!')
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
    print(Style.RESET_ALL + 'Saving responses...')
    responses_worksheet = SHEET.worksheet('responses')
    responses_worksheet.append_row(responses)


def analyze_data():
    """
    Calculates the percentage of respondants chosing each potential
    answer for each question.
    """
    print(Style.RESET_ALL + 'Analyzing data...')
    number_of_questions = get_number_of_questions()
    questions_worksheet = SHEET.worksheet('questions')
    responses_worksheet = SHEET.worksheet('responses')
    question_num = 1

    while question_num <= number_of_questions:
        print(f'Analysing Question {question_num} responses....')
        question_responses_col = responses_worksheet.col_values(question_num)
        question_responses = question_responses_col[1:]
        int_responses = [int(value) for value in question_responses]
        questions = questions_worksheet.col_values(question_num)
        number_of_answers = len(questions) - 2

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

        adjusted_percentages = adjust_percentages(percentages)
        print(f'Saving updated Question {question_num} analysis....')
        add_data_to_stats_worksheet(adjusted_percentages, question_num)

        question_num += 1

    print('\nAnalysis complete! Thank you!\n')
    print('Data worksheet can be viewed at:')
    print('https://docs.google.com/spreadsheets/d/')
    print('1VFA4T7ZKYnuBS6kPLoo7TUDiPYoVGaTs0z5zoFnYQh0/edit?usp=sharing')


def adjust_percentages(percentages):
    """
    Takes a list of calcuated percentages, finds the rounding error that
    leads to the list not adding to 100% and adds or subtracts this as
    appropriate from the largest percentage in the list.
    Returns a list of the adjusted percentages.
    """
    total = sum(percentages)
    roundby = round(100 - total, 1)
    indmax = percentages.index(max(percentages))
    replacement_val = round(percentages[indmax] + roundby, 1)
    percentages[indmax] = replacement_val

    return percentages


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
    print(Style.RESET_ALL + 'Retrieving survey analysis....\n')
    number_of_questions = get_number_of_questions()
    print(Fore.BLUE + 'When asked the following questions:\n')
    question_num = 1
    while question_num <= number_of_questions:
        question = get_question(question_num)
        stats = get_stats(question_num)
        display_question_format = question[1].split('#')
        last_index = len(display_question_format) - 1
        part = 0
        print(Fore.GREEN + f'Question {question_num}:')
        while part <= last_index:
            print(display_question_format[part])
            part += 1

        print(' \n')
        question_num += 1

        final_answer_index = len(question) - 1
        ans_ind = 2
        stats_index = 0

        while ans_ind <= final_answer_index:
            ans_num = ans_ind - 1
            print(Fore.CYAN + f'{stats[stats_index]}% of people replied:')
            print(Fore.BLUE + f'Answer {ans_num}: {question[ans_ind]}\n')
            ans_ind += 1
            stats_index += 1

    print(Style.RESET_ALL + 'Data worksheet can be viewed at:')
    print('https://docs.google.com/spreadsheets/d/')
    print('1VFA4T7ZKYnuBS6kPLoo7TUDiPYoVGaTs0z5zoFnYQh0/edit?usp=sharing')


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


if __name__ == '__main__':
    main()
