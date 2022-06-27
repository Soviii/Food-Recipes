import requests
import creds
import json
from recipe_model import Recipe

SPOONACULAR_HEADERS = {
    "x-api-key":creds.SPOONACULAR_API_KEY
}

RANDOM_RECIPE_ENDPOINT = "https://api.spoonacular.com/recipes/random"
# GET_RECIPE_INFORMATION_ENDPOINT = f"https://api.spoonacular.com/recipes/{id}/information"
# user_preferences = {"minCarbs":10}
# response = requests.get(url=RANDOM_RECIPE_ENDPOINT, headers=SPOONACULAR_HEADERS, params=user_preferences)
# response.raise_for_status()
# results = response.json()
# userRecipe = Recipe(results)

def requestRandomRecipe():
    global userRecipe
    response = requests.get(url=RANDOM_RECIPE_ENDPOINT, headers=SPOONACULAR_HEADERS)
    response.raise_for_status()
    results = response.json()
    userRecipe = Recipe(results)
    userRecipe.printEverything()
    
def showAllDishes():
    with open("history.json", "r") as file:
        data = json.load(file)
    #dictionary used for quality of life; allows user to not worry about case sensitivity when entering a dish
    dish_names = {}
    for meal in data.keys():
        print(meal)
        dish_names[meal.lower()] = meal
    
    user_input = input("Enter a name of one of the dishes or enter \"exit\" to go back to the main menu\n")
    done_with_func = False
    while True:
        user_input = user_input.lower()
        if user_input == "exit":
            done_with_func = True
            break
        elif user_input not in dish_names.keys():
            user_input = input("Error: dish not found locally. Please enter one listed from above\n")
        else:
            global userRecipe
            #converted data.keys() into a list since data.keys() is not subscriptable 
            name_of_recipe = dish_names[user_input]
            userRecipe = Recipe(results=data[name_of_recipe],name=name_of_recipe)
            print("Done!\n")
            done_with_func = True
            break

    return done_with_func
   

def recipeOption():
    global userRecipe

    OPTIONS = ["1", "save it locally", "2", "save it on google sheets", "3", "email it to myself", "4", "exit"]
    
    user_input = input(f"{userRecipe.recipe_details['title']} was selected. Would you like to:\n1)Save it locally\n2)Save it on Google Sheets\n3)Email it to yourself?\n4)Exit\n")
    user_input = user_input.lower()

    while user_input not in OPTIONS:
        user_input = user_input.lower()
        print("Error: invalid option, please type in the number of the following:\n")
        for index,option in enumerate(OPTIONS[1::2]):
            print(f"{index+1}. {option}")
        user_input = input("\n")
        user_input = user_input.lower()
        
    
    if user_input == "1" or user_input == "save it locally":
        userRecipe.saveRecipeLocally()
        if continueSending():
            recipeOption()
        else:
            pass
    elif user_input == "2" or user_input == "save it on google sheets":
        userRecipe.saveRecipeGoogleSheets()
        if continueSending(): 
            recipeOption()
        else: 
            pass
    elif user_input == "3" or user_input == "email it to myself":
        userRecipe.sendToEmail()
        if continueSending(): 
            recipeOption()
        else: 
            pass
    elif user_input == "4" or user_input == "exit":
        pass


def continueSending():
    user_input = input("Done!, Would you like to do another option? (Y or N)")
    user_input = user_input.upper()
    while user_input != "Y" and user_input != "N":
        user_input = input("Error: not a valid option, please enter \n")
        user_input.upper()
    return True if user_input == "Y" else False

#------------------------------------ Main Driver --------------------------------------------#
userRecipe = None
OPTIONS = ["1", "get random recipe", "2", "see saved recipes", "3", "exit"]
while True:
    user_input = input("Welcome to Sovi Meals! Please select an option:\n1) Get random recipe\n2) See saved recipes\n3) Exit\n")
    user_input = user_input.lower()
    userRecipe = None
    if user_input not in OPTIONS:
        print("Error: not a valid option, try again")
    
    else:
        if user_input == "1" or user_input == "get random recipe":
            requestRandomRecipe()
            recipeOption()
        
        elif user_input == "2" or user_input == "see saved recipes":
            continue_option = showAllDishes()
            if continue_option:
                recipeOption()
        
        elif user_input == "3" or user_input == "exit":
            print("Thank you for using Sovi Meals! Have a good day")
            break
    