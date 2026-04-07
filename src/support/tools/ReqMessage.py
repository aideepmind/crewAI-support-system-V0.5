
class ReqMessage:
    def __init__(self,userid,message):
        self.userid = userid
        self.message = message
    def print(self):
        print (self.userid)
        print (self.message)

class LLMContext:
    def __init__(self,userid):
        self.userid = userid

if __name__ == "__main__":
    t = ReqMessage("lys","abcd")
    t.print()
