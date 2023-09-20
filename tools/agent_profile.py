
class Profiling:

    def __init__(self,name="",background_story="", personality={}, duties="", missions="", motivations="",additional_info=""):
        self.name = name
        self.background_story = background_story
        self.personality = personality
        self.duties = duties
        self.missions = missions
        self.motivations = motivations
        self.additional_info = additional_info

    def introduction(self):
        intro = f"Hi, my name is {self.name}. "
        personality = [f"my {k} is {v}" for k, v in self.personality.items()]
        intro += f"To summarize, {','.join(personality)} "
        intro += f"I'm glad to share my story with you. My background is {self.background_story} "
        intro += f"My duties are responsible for {self.duties} and I am currently working for {self.missions}. "
        intro += f"My motivations for doing this work are {self.motivations}. "
        intro += f"In additionally, {self.additional_info}"
        return intro      

        def __str__(self):
            return self.introduction()

if __name__ == "__main__":
    def test_profile_introduction():
        profile = Profiling(
            name="John",
            background_story="I grew up in a small town in the midwest.",
            personality={
                "name": "John",
                "age": 30,
                "gender": "male",
                "hair_color": "brown",
                "eye_color": "blue",
                "hobbies": "playing guitar and hiking"
            },
            duties="managing a team of developers",
            missions="building a new software product",
            motivations="to create something that will make people's lives easier",
            additional_info="I'm looking for roommates to live togather."
        )
        expected_intro = "Hi, my name is John. To summarize, I am name is John,age is 30,gender is male,hair_color is brown,eye_color is blue. I'm glad to share my story with you. My background is I grew up in a small town in the midwest. My duties are responsible for managing a team of developers and I am currently working for building a new software product. My motivations for doing this work are to create something that will make people's lives easier. In additionally, "
        print(profile.introduction())

    test_profile_introduction()