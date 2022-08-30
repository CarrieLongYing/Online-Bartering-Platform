import web
import dbLogic
from datetime import date
from datetime import datetime

web.config.debug = False

urls = (
    '/', 'Home',
    '/login/', 'Login',
    '/logout/', 'Logout',
    '/registration/', 'Registration',
    '/mainmenu/', 'MainMenu',
    '/listitem/', 'Listitem',
    '/myitem/','Myitem',
    '/tradedetail/', 'TradeDetail',
    '/search/', 'Search',
    '/showItem/', 'ShowItem',
    '/selectItemDetail/', 'SelectItemDetail',
    '/proposetrade/', 'ProposeTrade',
    '/acceptrejecttrades/', 'AcceptRejectTrades',
    '/notification/', 'Notification',
    '/tradehistory/', 'TradeHistory',
    '/confirmtrade/', 'ConfirmTrade',
    '/ProposeTradeConfirmTrade/','ProposeTradeConfirmTrade'
    
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('session'))
globals = {'session': session}
render = web.template.render('webUI/', globals=globals, base='base')
renderNoBase = web.template.render('webUI/', globals=globals)




class Home:
    def GET(self):
        if session.get('username'):
            raise web.seeother('/mainmenu/')
        else:
            return render.login()

class AcceptRejectTrades:#have error when distance miles < 100
    def GET(self):
        # userEmail = 'a@gmail.com'
        counterpartyEmail = session.username
        #title name is duplicate
        proposedTrades = dbLogic.getProposedTrades(counterpartyEmail)
        # return proposedTrades
        return render.acceptrejecttrades(proposedTrades,None)
    
    def dateDiff(self,prev):
        date_format= "%Y-%m-%d"
        a = datetime.strptime(prev, date_format)
        today = date.today()
        b = datetime.strptime(str(today), date_format)
        delta = b - a
        return delta.days

    def POST(self):
        counterpartyEmail = session.username
        # inputData = web.input("/acceptrejecttrades/")
        inputData = web.input()

        print("-------------inputData----------------")
        print(inputData)
        if dbLogic.getNumOfPendingTrades(counterpartyEmail) == 0:
            raise web.seeother('/mainmenu/')
        if inputData.isAccept == "True":
            proposerEmail = inputData['Accept_proposer_email']

            tradeID = inputData.Accept_tradeID
            proposedDate = inputData.Accept_proposed_date
            responseTime = self.dateDiff(proposedDate)
            counterpartyRank = dbLogic.getRankByEmail(counterpartyEmail,True)
            proposerRank = dbLogic.getRankByEmail(counterpartyEmail,True)
            dbLogic.insertAcceptResponseTime(responseTime,tradeID)
            dbLogic.updateUserStatisticsForCounterparty(counterpartyEmail, responseTime, counterpartyRank)
            dbLogic.updateUserStatisticsForProposerWhenAccept(proposerEmail, proposerRank)
            return render.notification(proposerEmail)
        else:
            #reject，Unaccepted Trades does not update,it should minus 1
            proposerEmail = inputData['Reject_proposer_email']
            tradeID = inputData.Reject_tradeID
            proposedDate = inputData.Reject_proposed_date
            responseTime = self.dateDiff(proposedDate)
            counterpartyRank = dbLogic.getRankByEmail(counterpartyEmail, False)
            # proposerRank = dbLogic.getRankByEmail(counterpartyEmail,False)
            dbLogic.insertRejectResponseTime(responseTime,tradeID)
            dbLogic.updateUserStatisticsForCounterparty(counterpartyEmail, responseTime, counterpartyRank)
            dbLogic.updateUserStatisticsForProposerWhenReject(proposerEmail)
            raise web.seeother('/mainmenu/')


class Notification:
    def GET(self):
        return render.notification()

class ProposeTrade:#have error when distance miles < 100
    def POST(self):
        proposedData  = web.input()
        userEmail = session.username
        numOfPendingTrades = dbLogic.getPendingTrades(userEmail)
        counterpartyEmail = proposedData['counterparty_email']
        counterparty_itemID = proposedData["counterparty_itemID"]
        availableItems = dbLogic.viewAvailableItems(userEmail,counterparty_itemID)
        distance = dbLogic.getDistance(userEmail, counterpartyEmail)
        distanceWarning = False
        if distance >= 100:
            distanceWarning = True
        if numOfPendingTrades <= 1:
            proposedData  = web.input()
            return render.proposetrade(availableItems,distanceWarning,distance,proposedData)
        else:
            session.loginMessage("You have more than 1 pending trades, can not propose a new trade")
            raise web.seeother('/mainmenu/')

class ProposeTradeConfirmTrade:#have error when distance miles < 100
    def POST(self):
        inputData =  web.input()
        userEmail = session.username
        dbLogic.confirmTrade(userEmail,inputData["counterparty_email"],inputData["itemID"],inputData["counterparty_itemID"])
        dbLogic.updateUserStatisticsAfterConfirmTrade(inputData["counterparty_email"])
        return render.confirmtrade(inputData["counterparty_itemID"])

class ConfirmTrade:
    def GET(self):
        return render.confirmtrade()

    
class MainMenu:
    def GET(self):
        if session.get('username'):
            number_of_unaccepted_trade_counterparty, response_time, user_rank = dbLogic.getUserStats(session.username)
            first_name, last_name, nickname = dbLogic.getUserNames(session.username)
            return render.mainmenu(number_of_unaccepted_trade_counterparty, response_time, user_rank, first_name, last_name, nickname)
        else:
            raise render.login()


class Login:
    def GET(self):
        raise web.seeother('/')

    def POST(self):
        inputData = web.input()

        if dbLogic.isUser(inputData.username, inputData.password):
            session.loginMessage = 'Login Succeeds!'
            results = dbLogic.emailOrNickname(inputData.username)
            session.username, session.nickname = results
            print(results)
            raise web.seeother('/mainmenu/')
        else:
            session.loginMessage = 'User or Password Not Found!'
            raise web.seeother('/login/')


class Logout:
    def GET(self):
        if session:
            session.kill()
        raise web.seeother('/login/')


class Listitem:
    def GET(self):
        pending_item_counts = dbLogic.listItemQualify(session.username)
        session.listItemSuccessMessage = None
        if len(pending_item_counts) == 0 :
            return render.listitem()
        else:
            count = pending_item_counts[0]["number_of_unaccepted_trade_counterparty"]
            count = 0 if count is None else count
            if count < 2:
                return render.listitem()
            else:
                session.loginMessage = 'Please accept or reject your pending counterparty listing firstly!'
                raise web.seeother('/mainmenu/')


    def POST(self):
        inputData = web.input()
        print(session.username)
        itemId = dbLogic.insertItem(session.username,
                           inputData.title,
                           inputData.game_type,
                           inputData.item_condition,
                           inputData.description,
                           inputData.number_of_offered_card,
                           inputData.platform_type,
                           inputData.media
                           )

        session.listItemSuccessMessage = "Item " + str(itemId) + " listed!"
        return render.listitem()
        
    # def POST(self):
    #     inputData = web.input()
    #     dbLogic.insertUser(session.username,
    #                        inputData.title,
    #                        inputData.gametype,
    #                        inputData.itemcondition,
    #                        inputData.description,
    #                        inputData.number_of_offered_card):
    #     raise web.seeother('/mainmenu/')

class Myitem:
        def GET(self):
            itemCounts = {"Video Game": 0, "Playing Card Game": 0, "Collectible Card Game": 0, "Computer Game": 0, "Board Game": 0}
            myItemCounts = dbLogic.myItemCounts(session.username)

            for item in myItemCounts:
                itemCounts[item.game_type] = item.number_of_items
            
            total_count = sum([value for key, value in itemCounts.items()])
            myItemCounts2 = dbLogic.myItemCounts2(session.username)
        
            return render.myitem(itemCounts, total_count, myItemCounts2)

          
class Registration:
    def GET(self):
        return render.registration()

    def POST(self):
        inputData = web.input()
        if dbLogic.emailExists(inputData.email) or dbLogic.nicknameExists(inputData.nickname):
            session.registrationMessage = 'Email or Nickname Exists'
            raise web.seeother('/registration/')
        elif dbLogic.insertUser(inputData.email,
                                inputData.firstname,
                                inputData.lastname,
                                inputData.password,
                                inputData.nickname,
                                inputData.postalcode):
            session.registrationMessage = 'Registration is successful!'
            session.username = inputData.email
            raise web.seeother('/mainmenu/')
        else:
            session.registrationMessage = 'Registration is not Successful!'
            raise web.seeother('/registration/')


class TradeDetail:
    def POST(self):
        inputData = web.input()
        tradeID = inputData['tradeID']
        tradeInfo = dbLogic.getTradeDetail(session.username, tradeID)
        counterpartyInfo = dbLogic.getCounterPartyDetail(
            session.username, tradeID)
        proposed_item_info = dbLogic.getItemDetail(tradeID, 'proposed')
        desired_item_info = dbLogic.getItemDetail(tradeID, 'desired')
        return render.tradedetail(tradeInfo, counterpartyInfo, proposed_item_info, desired_item_info)
    
class TradeHistory:
    def GET(self):
        tradeSummary = dbLogic.getTradeHistorySummary(session.username)
        allTrades = dbLogic.getAllTradeHistory(session.username)
        return render.tradehistory(tradeSummary, allTrades)
 

class Search:
    def GET(self):
        return render.search()

    def POST(self):
        if (not session.get('username')):
            session.loginMessage = 'Login needed to search items!'
            return render.login()
        elif (web.input()["searchOption"]):
            inputData = web.input()
            currUserEmail = session.username
            if ((inputData['searchOption'] == "byKeyword") & (inputData['Keyword'] != "")):
                foundItems = dbLogic.searchByword(
                    currUserEmail, inputData['Keyword'])
                if len(foundItems) > 0:
                    searchOption = "keyword"
                    userInput = inputData['Keyword']
                    return render.searchResults(foundItems, searchOption, userInput)
                else:
                    session.naItemsFoundMsg = "Sorry, no results found!"
                    return render.search()
            elif (inputData['searchOption'] == "inMyPostalCode"):
                postal = dbLogic.findUserPostal(currUserEmail)
                postal = postal[0]["postal_code"]
                foundItems = dbLogic.searchInPostalcode(
                    currUserEmail, postal)
                if len(foundItems) > 0:
                    searchOption = "in my postal code"
                    userInput = ""
                    return render.searchResults(foundItems, searchOption, userInput)
                else:
                    session.naItemsFoundMsg = "Sorry, no results found!"
                    return render.search()
            elif (inputData['searchOption'] == "byPostal"):
                postal = inputData["byPostal"]
                ifValidPostal = dbLogic.ifValidPostal(postal)
                if (not ifValidPostal):
                    session.naItemsFoundMsg = "Sorry, the postal code entered is invalid!"
                    return render.search()
                foundItems = dbLogic.searchInPostalcode(
                    currUserEmail, postal)
                if len(foundItems) > 0:
                    searchOption = "in postal code"
                    userInput = inputData["byPostal"]
                    return render.searchResults(foundItems, searchOption, userInput)
                else:
                    session.naItemsFoundMsg = "Sorry, no results found!"
                    return render.search()
            elif (inputData['searchOption'] == "withinXMiles"):
                withinXMiles = inputData["byDistance"]
                foundItems = dbLogic.searchWithinXMiles(
                    currUserEmail, withinXMiles)
                if len(foundItems) > 0:
                    searchOption = "Within miles"
                    userInput = inputData["byDistance"]
                    return render.searchResults(foundItems, searchOption, userInput)
                else:
                    session.naItemsFoundMsg = "Sorry, no results found!"
                    return render.search()
            else:
                session.naItemsFoundMsg = "Sorry, no results found!"
                return render.search()
        else:
            session.naItemsFoundMsg = "Sorry, no results found!"
            return render.search()

class SelectItemDetail:
    def POST(self):
        inputData = web.input()
        itemDeatils = dbLogic.searchItemByID(inputData["itemID"])
        itemBelongsTo = itemDeatils[0]["user_email"]
        currUserEmail = session.username
        if web.input()["notDisplay"]== "notDisplay":
            ifProposeTrade = False
        else: ifProposeTrade = True
        if (itemBelongsTo == currUserEmail):
            userDetails = "notDisplay"
        else: 
            userDetails = dbLogic.searchUserDetailByEmail(itemBelongsTo, currUserEmail)
        itemDeatils = dbLogic.searchItemByID(inputData["itemID"])
        return render.showItem(itemDeatils, userDetails, ifProposeTrade)


class ShowItem:
    def GET(self):
        return render.showItem(6)



if __name__ == "__main__":
    app.run()
