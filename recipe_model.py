import re
import json
import requests
import creds
import smtplib


class Recipe():
    def __init__(self, results, name=""):
        #if recipe is chosen from local file
        if name:
            self.recipe_details = {
                    "title": name,
                }
            self.recipe_details.update(results)
            
        #if recipe is chosen from API's endpoint 
        else:
            self.recipe_details = {
                "title": results["recipes"][0]["title"],
                "id": results["recipes"][0]["id"],
                "summary": self.cleanHTML(results["recipes"][0]["summary"]),
                "healthy": "Yes" if results["recipes"][0]["veryHealthy"] else "No", 
                "type of dish": [dish for dish in results["recipes"][0]["dishTypes"]],
                "time to finish": results["recipes"][0]["readyInMinutes"],
                "vegetarian": "Yes" if results["recipes"][0]["vegetarian"] else "No",
                "vegan": "Yes" if results["recipes"][0]["vegan"] else "No",
                "cheap": "Yes" if results["recipes"][0]["cheap"] else "No",
                "popular": "Yes" if results["recipes"][0]["veryPopular"] else "No",
                "ingredients": self.listIngredients(results["recipes"][0]["extendedIngredients"]),
                "instructions": self.listInstructions(results["recipes"][0]["analyzedInstructions"]),  
            }
        

    #!Design getting price of recipe https://spoonacular.com/food-api/docs#Price-Breakdown-by-ID
    #!Add functionality for getting video for it https://spoonacular.com/food-api/docs#Search-Food-Videos
    
    #Function is necessary in the case that there are no instructions listed
    def listInstructions(self, instruction_steps=[])->list:
        try:
            if len(instruction_steps[0]["steps"]) == 0:
                return ["N/A"]
            return [f"{number+1}. {instructions['step']}" for number,instructions in enumerate(instruction_steps[0]["steps"])]

        except IndexError:
            return ["N/A"]
    
    #Function is necessary in the case that there are no instructions listed
    def listIngredients(self, ingredient_list=[]):
        try:
            if len(ingredient_list) == 0:
                return ["N/A"]
            return [ingredient["original"] for ingredient in ingredient_list]
        
        except IndexError:
            return ["N/A"]
        

    def printEverything(self):
        for key,value in self.recipe_details.items():
            print(f"{key}: {value}")
    

    def cleanHTML(self, raw_html):
        CLEANR = re.compile('<.*?>')
        cleantext = re.sub(CLEANR, '', raw_html)
        return cleantext
    

    def saveRecipeLocally(self):
        new_info = {
            self.recipe_details["title"]: {
                key:value for key,value in dict(list(self.recipe_details.items())[1:]).items()
            }
        }
        try:
            with open("history.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            with open("history.json", "a") as file:
                data = json.dump(new_info, file, indent=4)
        else: 
            with open("history.json", "w") as file:
                data.update(new_info)
                json.dump(data, file, indent=4)

    def saveRecipeGoogleSheets(self):
        sheety_endpoint = "https://api.sheety.co/7df527968a3e5b962316b7639c114e67/myRecipes/sheet1"
        googlesheets_details = {
            "sheet1":{
                key:str(value) for key,value in self.recipe_details.items()
                #!change how types of dish, ingredients, instructions are provided
            }
        }
        sheety_response = requests.post(url=sheety_endpoint, json=googlesheets_details, auth=(creds.SHEETY_API_USERNAME, creds.SHEETY_API_PASSWORD))
        sheety_response.raise_for_status()
        print("Success!")
    
    def sendToEmail(self):
        def returnAllTypes():
            types = ""
            for type in self.recipe_details:
                types += f"{type}, "
            return types[:len(types)-2]
        
        def returnIngredients():
            ingredients = ""
            for ingredient in self.recipe_details['ingredients']:
                ingredients = f"{ingredient}, "
            return ingredients[:len(ingredients)-2]
        
        def returnInstructions():
            instructions = "Instructions:\n"
            num_of_instruction = 1
            for instruction in self.recipe_details["instructions"]:
                instructions += f"{num_of_instruction}. {instruction}\n"
                num_of_instruction += 1
            return instructions

        user_address = input("Enter your email address\n")
        email_formatted_details = f"""
{self.recipe_details['title']}\n
Recipe ID Number:{self.recipe_details['id']}\n
{self.recipe_details['summary']}\n
{"Healthy" if self.recipe_details['healthy'] == "Yes" else "Not Healthy"}\n
Details of dish: {returnAllTypes()}\n
{self.recipe_details['time to finish']} minutes\n
{"Vegetarian" if self.recipe_details['vegetarian'] == "Yes" else "Not Vegetarian"}\n
{"Vegan-friendly" if self.recipe_details['vegan'] == "Yes" else "Not vegan-friendly"}\n
{"Cheap" if self.recipe_details['cheap'] == "Yes" else "Expensive"}\n
{"Popular" if self.recipe_details['popular'] == "Yes" else "Not Popular"}\n
{returnIngredients()}\n
{returnInstructions()}\n
"""
        try:
            with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                connection.starttls()
                connection.login(user=creds.EMAIL_ADDRESS, password=creds.EMAIL_PASSWORD)
                connection.sendmail(
                    from_addr=creds.EMAIL_ADDRESS,
                    to_addrs=user_address,
                    msg=f"Subject:New Recipe Inbound!👨‍🍳😋\n\n{email_formatted_details}".encode('utf8')
                )
                connection.close()
        except: print("Error: invalid email address")
        else: print("Success!")

        
        
