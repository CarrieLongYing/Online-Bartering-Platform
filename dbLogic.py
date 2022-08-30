import web
from datetime import datetime
from enum import Enum

# dbConn = web.database(
#     dbn='mysql', db='cs6400_summer22_team040', user='root', pw='root')
dbConn = web.database(dbn='mysql', db='cs6400_summer22_team040', user='root', pw='root', host='localhost') 



class TradeStatus(Enum):
    ACCEPTED = '1' 
    PENDING =  '2' 
    REJECTED = '0'
def getPendingTrades(email):
    sql = """
        SELECT number_of_unaccepted_trade_counterparty
        FROM userstatistics
        WHERE email = $email
    """
    vars = {
        'email' : email
    }
    results = dbConn.query(sql, vars = vars)
    num = results[0]['number_of_unaccepted_trade_counterparty']
    return num


def viewAvailableItems(email, counterparty_itemID):
    sql = """
        SELECT itemID,game_type,title,item_condition 
        FROM Item 
		WHERE user_email = $email
        AND itemID NOT IN (SELECT proposed_itemID FROM Trade WHERE trade_status = "1" or trade_status = "2")
        AND itemID NOT IN
                    (SELECT proposed_itemID
                    FROM Trade
                    WHERE trade_status = "1"
                    OR trade_status = "2"
                    UNION
                    SELECT desired_itemID
                    FROM Trade
                    WHERE trade_status = "1"
                    OR trade_status = "2")
        AND itemID NOT IN 
                    (SELECT proposed_itemID
                    FROM Trade
                    WHERE desired_itemID = $counterparty_itemID
                    AND trade_status = "0"
                    )
    """
    vars = {
        'email' : email,
        'counterparty_itemID' : counterparty_itemID
    }
    results = dbConn.query(sql, vars = vars)
    return results

def getDistance(proposerEmail, counterpartyEmail):
    sql = """
        SELECT ROUND(distance, 2) AS distance
        FROM Distance 
        WHERE postal_code_from = (SELECT postal_code FROM User WHERE User.email = $CounterPartyEmail)
        AND Distance.postal_code_to = 
        (SELECT postal_code FROM User WHERE User.email=$Email) 

    """
    vars = {
        'CounterPartyEmail' : counterpartyEmail,
        'Email': proposerEmail,
    }

    results = dbConn.query(sql, vars = vars)
    return results[0]['distance']

def getItemsByID(itemID):
    sql = """
        SELECT * 
        FROM Item 
        WHERE itemID  = $itemID
    """
    vars = {
        'emitemID ail' : itemID 
    }
    results = dbConn.query(sql, vars = vars)
    return results

def confirmTrade(proposerEmail, counterpartyEmail, proposedItemID, desiredItemID):
    print("-------confirmTrade----------")
    print(TradeStatus.PENDING.value)
    sql = """
        INSERT  INTO  Trade (proposer_email, counterparty_email, proposed_itemID, desired_itemID, proposed_date, trade_status)
        VALUES ( $ProposerEmail, $CounterpartyEmail, $ProposedItemID,$DesiredItemID,$DateTime, $TradeStatus);
    """
    vars = {
        'DateTime' : datetime.now(),
        'TradeStatus' : TradeStatus.PENDING.value,
        'ProposerEmail' : proposerEmail,
        'CounterpartyEmail' : counterpartyEmail,
        'ProposedItemID' : proposedItemID,
        'DesiredItemID' : desiredItemID
    }
    results = dbConn.query(sql, vars = vars)
    return results


def updateUserStatisticsAfterConfirmTrade(counterpartyEmail):
    sql = """
        UPDATE userstatistics 
            SET number_of_unaccepted_trade_counterparty = 1 + number_of_unaccepted_trade_counterparty 
        WHERE email=$CounterpartyEmail;
    """
    vars = {
        'CounterpartyEmail' : counterpartyEmail

    }
    results = dbConn.query(sql, vars = vars)
    print("results----------------------------")
    print(results)
    return results

def getProposedTrades(counterPartyEmail):
    sql = """
        SELECT
        t.proposer_email,
        t.proposed_itemID,
        t.desired_itemID,
        t.proposed_date,
        t.tradeID,
        i.title as proposedTitle,
        u.nickname,
        us.user_rank,
        ROUND(d.distance, 2) AS distance,
        i2.title as desiredTitle
        FROM Trade t
        LEFT JOIN Item i
        ON t.proposed_itemID = i.itemID
        LEFT JOIN User u
        ON t.proposer_email = u.email
        LEFT JOIN UserStatistics us
        ON t.counterparty_email = us.email
        LEFT JOIN Distance d
        ON d.postal_code_from = u.postal_code AND d.postal_code_to = 
        (SELECT postal_code FROM User WHERE User.email = $Email)
        LEFT JOIN Item i2
        ON t.desired_itemID = i2.itemID       
        WHERE t.counterparty_email = $Email AND t.trade_status = '2'

    """

    vars = {
        'Email' : counterPartyEmail
    }
    results = dbConn.query(sql, vars = vars)

    return results

def getNumOfCompletedTradesByEmail(email):
    sql = """
        SELECT (number_of_completed_trade_counterparty + number_of_completed_trade_proposer) as sum
        FROM UserStatistics  
        WHERE email = $Email
    """
    vars = {
        'Email' : email 
    }
    results = dbConn.query(sql, vars = vars)
    return results[0]['sum']


def getRankByEmail(email, isAccepted):
    if isAccepted:
        numOfCompletedTrades = getNumOfCompletedTradesByEmail(email) + 1
    else:
        numOfCompletedTrades = getNumOfCompletedTradesByEmail(email) 

    if numOfCompletedTrades == 0:
        return None
    elif numOfCompletedTrades <= 2:
        return 'Aluminium'
    elif numOfCompletedTrades <= 3:
        return 'Bronze'       
    elif numOfCompletedTrades <= 5:
        return 'Silver'
    elif numOfCompletedTrades <= 7:
        return 'Gold'
    elif numOfCompletedTrades <= 9:
        return 'Platinum'
    else:
        return 'Alexandinium'

def getProposerInfo(email):
    
    sql = """
        SELECT 
        proposer_email,
        first_name 
        FROM Trade INNER JOIN User 
        ON Trade.proposer_email = User.email 
        WHERE Trade.counterparty_email = $CounterPartyEmail
        """
    vars = {
        'CounterPartyEmail' : email 
    }
    results = dbConn.query(sql, vars = vars)
    return results



def getTradeProposedDate(proposerEmail,counterPartyEmail, proposedItemID, desiredItemID):

    sql = """
        SELECT proposed_date FROM Trade 
        WHERE 
        proposer_email=$ProposerEmail AND counterparty_email=$CounterPartyEmail AND proposed_itemID=$ProposedItemID AND 
        desired_ItemID=$DesiredItemID

        """
    vars = {
        'ProposerEmail' : proposerEmail,
        'CounterPartyEmail' : counterPartyEmail, 
        'ProposedItemID' : proposedItemID, 
        'DesiredItemID' : desiredItemID, 

    }
    results = dbConn.query(sql, vars = vars)
    return results

def insertAcceptResponseTime(responseTime,tradeID):

    sql = """
        UPDATE trade SET trade_status = $tradeStatus, 
        accepted_rejected_date=$Datetime, response_time=$responseTime WHERE tradeID = $tradeID;
        """
    vars = {
        'tradeStatus' : TradeStatus.ACCEPTED.value,
        'Datetime' : datetime.now(), 
        'responseTime' : responseTime,
        'tradeID' : tradeID
    }
    results = dbConn.query(sql, vars = vars)
    return results != None

def insertRejectResponseTime(responseTime,tradeID):

    sql = """
        UPDATE trade SET trade_status = $tradeStatus, 
        accepted_rejected_date=$Datetime, response_time=$responseTime WHERE tradeID = $tradeID;
        """
    vars = {
        'tradeStatus' : TradeStatus.REJECTED.value,
        'Datetime' : datetime.now(), 
        'responseTime' : responseTime,
        'tradeID' : tradeID
    }
    results = dbConn.query(sql, vars = vars)
    return results != None

def getNumOfPendingTrades(counterPartyEmail):
    sql = """
        SELECT number_of_unaccepted_trade_counterparty FROM userstatistics WHERE email = $CounterPartyEmail;

        """
    vars = {

        'CounterPartyEmail' : counterPartyEmail

    }
    results = dbConn.query(sql, vars = vars)
    return results[0]['number_of_unaccepted_trade_counterparty']


def updateUserStatisticsForCounterparty (counterPartyEmail,responseTime, rank):

    sql = """
        UPDATE UserStatistics 
        SET user_rank=$rank, response_time = ((response_time * number_of_completed_trade_counterparty +  $ResponseTime) / (number_of_completed_trade_counterparty + 1)),
        number_of_unaccepted_trade_counterparty = number_of_unaccepted_trade_counterparty - 1
        WHERE email=$CounterPartyEmail;
        """
    vars = {
        'ResponseTime' :responseTime,
        'CounterPartyEmail' : counterPartyEmail,
        'rank' : rank

    }
    results = dbConn.query(sql, vars = vars)
    return results != None

def updateUserStatisticsForProposerWhenAccept(proposerEmail,rank):
    sql = """
            UPDATE UserStatistics 
            SET user_rank=$rank, number_of_completed_trade_proposer = 1 + number_of_completed_trade_proposer,
            number_of_unaccepted_trade_counterparty = number_of_unaccepted_trade_counterparty - 1
            WHERE email=$proposerEmail
            """
       
    vars = {
        'proposerEmail' : proposerEmail,
        'rank' : rank
    }
    results = dbConn.query(sql, vars = vars)
    return results != None


def updateUserStatisticsForProposerWhenReject(proposerEmail):

    sql = """
            UPDATE UserStatistics 
            SET 
            number_of_unaccepted_trade_counterparty = number_of_unaccepted_trade_counterparty - 1
            WHERE email=$proposerEmail
            """
    vars = {
        'proposerEmail' : proposerEmail,
    }
    results = dbConn.query(sql, vars = vars)
    return results != None





def getNumOfPendingTrades(counterPartyEmail):
        # SELECT count(*) FROM trade WHERE trade_status = '0' AND counterparty_email = $counterPartyEmail;

    sql = """
        SELECT number_of_unaccepted_trade_counterparty FROM cs6400_summer22_team040.userstatistics WHERE email = $counterPartyEmail;
        """
    vars = {
        'counterPartyEmail' : counterPartyEmail
            }
    results = dbConn.query(sql, vars = vars)
    return results


def isUser(username, password):
    sql = """
        SELECT email, password FROM User WHERE email = $username
        UNION
        SELECT nickname AS email, password FROM User WHERE nickname = $username
    """

    vars = {
        'username': username
    }

    results = dbConn.query(sql, vars=vars)

    for record in results:
        if record['email'] == username and record['password'] == password:
            return True
    else:
        return False


def emailOrNickname(username):
    sql = """
        SELECT email, nickname FROM User WHERE email = $username
        UNION
        SELECT email, nickname FROM User WHERE nickname = $username
    """

    vars = {
        'username': username
    }

    results = dbConn.query(sql, vars=vars)
    email = None
    nickname = None
    for record in results:
        email, nickname = record['email'], record['nickname']
    return email, nickname


def insertUser(email,
               firstname,
               lastname,
               password,
               nickname,
               postalcode):

    sql = """
        INSERT  INTO  User (email, first_name, last_name, password, nickname, postal_code)
        VALUES ( $email, $firstname,  $lastname,  $password,  $nickname , $postalcode);
    """

    vars = {
        'email': email,
        'firstname': firstname,
        'lastname': lastname,
        'password': password,
        'nickname': nickname,
        'postalcode': postalcode
    }

    userResult = dbConn.query(sql, vars=vars)

    sql = """
        INSERT  INTO  UserStatistics (email, number_of_completed_trade_proposer, number_of_completed_trade_counterparty, response_time, number_of_unaccepted_trade_counterparty, user_rank)
        VALUES ( $email, NULL , NULL , NULL , NULL  , 'None');
    """
    vars = {
        'email': email
    }

    statsResult = dbConn.query(sql, vars=vars)

    return (userResult != None) and (statsResult != None)


def emailExists(email):
    sql = """
        SELECT email FROM User WHERE email = $email
    """
    vars = {
        'email': email
    }

    results = dbConn.query(sql, vars=vars)
    return len(results) > 0


def nicknameExists(nickname):
    sql = """
        SELECT nickname FROM User WHERE nickname = $nickname
    """
    vars = {
        'nickname': nickname
    }

    results = dbConn.query(sql, vars=vars)
    return len(results) > 0


def listItemQualify(username):

    sql = """
       SELECT number_of_unaccepted_trade_counterparty
       FROM UserStatistics 
       WHERE email = $username
    """
    vars = {
        'username': username
    }

    results = dbConn.query(sql, vars=vars)
    return results

def insertItem(username,
                 title,
                 game_type,
                 item_condition,
                 description,
                 number_of_offered_card,
                 platform_type,
                 media
                 ):
             
    sql = """
         INSERT  INTO  Item(title,item_condition,description,user_email,game_type)
         VALUES ( $title, $item_condition,  $description,  $username,  $game_type);
     """
    vars = {
            'title': title,
            'item_condition': item_condition,
            'description': description,
            'username': username,
            'game_type': game_type
        }

    dbConn.query(sql, vars=vars)

    lastId = dbConn.query("SELECT LAST_INSERT_ID() as last_insert_id;")[0].last_insert_id
    if game_type == 'Computer Game':
        cgsql = """
            INSERT INTO ComputerGame (itemID, platform_type)
            VALUES ($lastId,$platform_type)
            ;
        """
        vars = {
                'lastId': lastId,
                'platform_type': platform_type
            }
        dbConn.query(cgsql, vars=vars)
        
    if game_type == 'Video Game':
        vgsql = """
            INSERT INTO VideoGame (itemID, platform_type,media)
            VALUES ($lastId,$platform_type,$media)
            ;
        """
        vars = {
                'lastId': lastId,
                'platform_type': platform_type,
                'media':media
            }
        dbConn.query(vgsql, vars=vars)
    if game_type == 'Collectible Card Game':
        ccgsql = """
            INSERT INTO collectiableCardGame (itemID, number_of_offered_card)
            VALUES ($lastId,$number_of_offered_card)
            ;
        """
        vars = {
                'lastId': lastId,
                'number_of_offered_card': number_of_offered_card
            }
        dbConn.query(ccgsql, vars=vars)
    return lastId

def myItemCounts(username):
    sql = """
        SELECT game_type
             , COUNT(itemID) as number_of_items
        FROM Item
        WHERE user_email = $username
        GROUP BY game_type
    """
    vars = {
        'username': username
    }
    results = dbConn.query(sql, vars = vars)
    return results

def myItemCounts2(username):
    sql = """
        SELECT itemID
        , game_type
        , title
        , item_condition
        , CASE WHEN LENGTH(description) > 100 THEN CONCAT(SUBSTRING(description, 1, 100),'...') ELSE description END AS description
        FROM Item
        WHERE user_email = $username
    """
    vars = {
        'username': username
    }
    results = dbConn.query(sql, vars = vars)
    return results

def getItemDetail(trade_id, item_type):
    if item_type == 'proposed':
        sql = """
            SELECT
                itemID,
                title,
                game_type,
                item_condition,
                description
            FROM Item WHERE Item.itemID = (SELECT proposed_itemID FROM Trade WHERE TradeID = $trade_id)
        """
    else:
        sql = """
            SELECT
                itemID,
                title,
                game_type,
                item_condition,
                description
            FROM Item WHERE Item.itemID = (SELECT desired_itemID FROM Trade WHERE TradeID = $trade_id)
        """

    vars = {
        'trade_id': trade_id
    }

    results = dbConn.query(sql, vars = vars)
    return results


def getCounterPartyDetail(email, tradeID):
    sql = """
        SELECT 
            nickname AS Nickname,
            User.first_name AS Name,
            (SELECT ROUND(distance, 2) FROM Distance
                WHERE Distance.postal_code_from = (SELECT postal_code FROM User WHERE User.email= (SELECT proposer_email AS email 
                                    FROM Trade
                                    WHERE tradeID = $tradeID AND proposer_email != $email
                                    UNION 
                                    SELECT counterparty_email AS email 
                                    FROM Trade
                                    WHERE tradeID = $tradeID AND counterparty_email != $email) )
                    AND Distance.postal_code_to = (SELECT postal_code FROM User WHERE User.email= $email)
            ) AS Distance,
            email AS Email
        FROM User
        WHERE User.email= (SELECT proposer_email AS email 
                                    FROM Trade
                            WHERE tradeID = $tradeID AND proposer_email != $email
                            UNION 
                            SELECT counterparty_email AS email 
                            FROM Trade
                            WHERE tradeID = $tradeID AND counterparty_email != $email)
    """

    vars = {
        'email': email,
        'tradeID': tradeID
    }

    results = dbConn.query(sql, vars = vars)
    return results


def getTradeDetail(email, trade_id):
    sql = """
        SELECT
            proposed_date,
            accepted_rejected_date,
            CASE 
                WHEN trade_status = '1' THEN "Accepted"
                WHEN trade_status = '0' THEN "Rejected"
                ELSE "Pending" 
            END AS trade_status,		
            'Proposer' AS my_role, 
            ROUND(response_time, 1) as response_time
        FROM Trade
        WHERE Trade.tradeID = $trade_id
        AND Trade.proposer_email = $email
        UNION
        SELECT
            proposed_date,
            accepted_rejected_date,
            CASE 
                WHEN trade_status = '1' THEN "Accepted"
                WHEN trade_status = '0' THEN "Rejected"
                ELSE "Pending" 
            END AS trade_status,				
            'Counterparty' AS my_role, 
            ROUND(response_time, 2) as response_time
        FROM Trade
        WHERE Trade.tradeID = $trade_id
        AND Trade.counterparty_email = $email
    """

    vars = {
        'email': email,
        'trade_id': trade_id
    }

    results = dbConn.query(sql, vars = vars)
    return results

def getTradeHistorySummary(email):
    sql = """
    SELECT A.my_role,
        SUM(A.accepted)+SUM(A.rejected) as total,
        SUM(A.accepted) as accepted,
        SUM(A.rejected) as rejected,
        ROUND(SUM(A.rejected) / (SUM(A.accepted)+SUM(A.rejected))*100,1) as rejected_percent
    FROM
        (SELECT
        CASE WHEN T.proposer_email = $email THEN "Proposer" ELSE "Counterparty" END AS my_role,
        CASE WHEN T.trade_status= "1" THEN 1 ELSE 0 END AS accepted,
        CASE WHEN T.trade_status= "0" THEN 1 ELSE 0 END AS rejected
        FROM Trade AS T
        WHERE T.proposer_email = $email OR T.counterparty_email = $email
        ) AS A
    GROUP BY A.my_role;
    """

    vars = {
        'email' : email
    }

    results = dbConn.query(sql, vars = vars)
    return results

def getAllTradeHistory(email):
    sql = """
        SELECT
			B.proposed_date,
			B.accepted_rejected_date,
			CASE WHEN B.trade_status="1" THEN "Accepted"
            ELSE "Rejected" END AS trade_status,
			ROUND(B.response_time,0) as response_time,
			B.my_role,
			C.title as proposed_item,
			D.title as desired_item,
			B.other_user,
            B.tradeID
        FROM ( 
			SELECT
			T.*,
			"Proposer" AS my_role,
			U.nickname AS other_user
			FROM Trade AS T
			INNER JOIN User AS U
			ON U.email=T.counterparty_email
			WHERE T.proposer_email = $email
			UNION
			SELECT
			T.*,
			"Counterparty" AS my_role,
			U.nickname AS other_user
			FROM Trade AS T
			INNER JOIN User AS U
			ON U.email=T.proposer_email
			WHERE T.counterparty_email = $email
			) AS B
        LEFT JOIN Item AS C
			on B.proposed_itemID=C.itemID
        LEFT JOIN Item AS D
			on B.desired_itemID=D.itemID
		WHERE B.trade_status in ("1", "0")
        ORDER BY B.accepted_rejected_date DESC, proposed_date ASC;
    """

    vars = {
        'email' : email
    }

    results = dbConn.query(sql, vars = vars)
    return results



def getUserStats(email):
    sql = """
        SELECT 
            number_of_unaccepted_trade_counterparty,
            response_time,
            user_rank
        FROM UserStatistics
        WHERE email=$email;
    """
    vars = {
        'email' : email
    }

    results = dbConn.query(sql, vars = vars)
    for record in results:
        number_of_unaccepted_trade_counterparty = record['number_of_unaccepted_trade_counterparty']
        response_time = record['response_time']
        user_rank = record['user_rank']
    return number_of_unaccepted_trade_counterparty, response_time, user_rank


def getUserNames(email):
    sql = """
        SELECT
        first_name,
        last_name,
        nickname
        FROM User
        WHERE email = $email;
    """
    vars = {
        'email' : email
    }

    results = dbConn.query(sql, vars = vars)
    for record in results:
        first_name = record['first_name']
        last_name = record['last_name']
        nickname = record['nickname']
    return first_name, last_name, nickname


#Author: Carrie Long
def searchByword(curUserEmail, search):
    sql = """
        SELECT
            I.itemID,I.game_type, I.title, I.item_condition, I.description,
            ROUND(S.response_time, 1) AS response_time, S.user_rank, ROUND(distance.distance,2) AS distance
        FROM Item AS I
        INNER JOIN
            (SELECT itemID, user_email
            FROM Item
            WHERE
                (title LIKE $search
                OR description LIKE $search)
            AND itemID NOT IN
                (SELECT proposed_itemID
                FROM Trade
                WHERE trade_status = "1"
                OR trade_status = "2"
                UNION
                SELECT desired_itemID
                FROM Trade
                WHERE trade_status = "1"
                OR trade_status = "2")
            ) AS F
        ON I.itemID = F.itemID
        INNER JOIN UserStatistics AS S
        ON I.user_email = S.email
        INNER JOIN User AS U
        ON U.email = I.user_email
        INNER JOIN
				(SELECT distance, postal_code_to
                FROM Distance
                WHERE Distance.postal_code_from =
                    (SELECT postal_code
                    FROM User
                    WHERE User.email= $curUserEmail)
                AND Distance.postal_code_to IN
                    (SELECT postal_code
                    FROM User
                    WHERE User.email IN
                        (SELECT user_email
                        FROM Item
                        WHERE
                            (itemID LIKE $search
                            OR game_type LIKE $search
                            OR title LIKE $search
                            OR item_condition LIKE $search
                            OR description LIKE $search)
                        AND itemID NOT IN
                            (SELECT proposed_itemID
                            FROM Trade
                            WHERE trade_status = "1"
                            OR trade_status = "2"
                            UNION
                            SELECT desired_itemID
                            FROM Trade
                            WHERE trade_status = "1"
                            OR trade_status = "2")))) AS distance
		ON U.postal_code = distance.postal_code_to
        WHERE I.user_email != $curUserEmail
        ORDER BY distance.distance, I.itemID
        """
    vars = {'search': '%' + search + '%',
            'curUserEmail': curUserEmail}

    results = dbConn.query(sql, vars=vars)
    return results

def ifValidPostal(postal):
    sql = """
        SELECT COUNT(*) AS num
        FROM User
        WHERE User.postal_code= $postal
    """
    vars = {'postal': postal}

    results = dbConn.query(sql, vars=vars)
    resultsNum = results[0]["num"]

    return resultsNum > 0

def findUserPostal(curUserEmail):
    sql = """
        SELECT postal_code
        FROM User
        WHERE User.email= $curUserEmail
    """
    vars = {'curUserEmail': curUserEmail}

    results = dbConn.query(sql, vars=vars)
    return results


def searchInPostalcode(curUserEmail, postal):
    sql = """
        SELECT
            I.itemID,I.game_type, I.title, I.item_condition, I.description,
             ROUND(S.response_time,1) AS response_time, S.user_rank, ROUND(distance.distance,2) AS distance
        FROM Item AS I
        INNER JOIN UserStatistics AS S
        ON I.user_email = S.email
        INNER JOIN User AS U
        ON U.email = I.user_email
        INNER JOIN
				(SELECT distance, postal_code_to
                FROM Distance
                WHERE Distance.postal_code_from =
                    (SELECT postal_code
                    FROM User
                    WHERE User.email= $curUserEmail)
                AND Distance.postal_code_to IN
                    (SELECT postal_code
                    FROM User
                    WHERE postal_code = $postal)) AS distance
		ON U.postal_code = distance.postal_code_to
		WHERE U.postal_code = $postal
        AND I.user_email != $curUserEmail
        AND I.itemID NOT IN
                    (SELECT proposed_itemID
                    FROM Trade
                    WHERE trade_status = "1"
                    OR trade_status = "2"
                    UNION
                    SELECT desired_itemID
                    FROM Trade
                    WHERE trade_status = "1"
                    OR trade_status = "2")
        ORDER BY distance.distance, I.itemID;
        """
    vars = {'postal': postal,
            'curUserEmail': curUserEmail}

    results = dbConn.query(sql, vars=vars)
    return results


def searchWithinXMiles(curUserEmail, withinXMiles):
    sql = """
       	SELECT
            I.itemID,I.game_type, I.title, I.item_condition, I.description,
             ROUND(S.response_time,1) AS response_time, S.user_rank, ROUND(foundEmailDistance.distance,2) AS distance
        FROM Item AS I
        INNER JOIN UserStatistics AS S
        ON I.user_email = S.email
        INNER JOIN User AS U
        ON U.email = I.user_email
        INNER JOIN 
            (SELECT User.email, foundPostalTo.distance
            FROM User
            INNER JOIN
                (SELECT distance, postal_code_to
                FROM Distance
                WHERE Distance.postal_code_from IN
                    (SELECT postal_code
                    FROM User
                    WHERE User.email= $curUserEmail)
                AND distance < $withinXMiles) AS foundPostalTo
			ON User.postal_code = foundPostalTo.postal_code_to) AS foundEmailDistance
		ON U.email = foundEmailDistance.email
        WHERE I.user_email != $curUserEmail
        AND I.itemID NOT IN
            (SELECT proposed_itemID
            FROM Trade
            WHERE trade_status = "1"
            OR trade_status = "2"
            UNION
            SELECT desired_itemID
            FROM Trade
            WHERE trade_status = "1"
            OR trade_status = "2")
        ORDER BY foundEmailDistance.distance, I.itemID
    """
    vars = {'withinXMiles': withinXMiles,
            'curUserEmail': curUserEmail}

    results = dbConn.query(sql, vars=vars)
    return results


def searchItemByID(itemID):
    sql = """
       	SELECT
            I.itemID, I.title, I.game_type, I.item_condition, I.description,
            V.platform_type AS platform_type_V, V.media,
            CC.number_of_offered_card,
            C.platform_type AS platform_type_C,
            I.user_email
        FROM Item AS I
        LEFT JOIN VideoGame AS V
        ON I.itemID = V.itemID
        LEFT JOIN CollectiableCardGame AS CC
        ON I.itemID = CC.itemID
        LEFT JOIN ComputerGame AS C
        ON I.itemID = C.itemID
		WHERE I.itemID = $itemID
    """
    vars = {'itemID': itemID}

    results = dbConn.query(sql, vars=vars)
    return results

def searchUserDetailByEmail(itemBelongsTo, curUserEmail):
    sql = """
        SELECT U.email, U.nickname, U.Postal_code,
	        P.city, P.state,
	        S.response_time, S.user_rank, ROUND(D.distance,2) AS distance
        FROM user AS U
        INNER JOIN PostalCode AS P
        ON U.postal_code = P.postal_code
        INNER JOIN UserStatistics AS S
        ON U.email = S.email
        INNER JOIN (SELECT distance, postal_code_to
                FROM Distance
                WHERE Distance.postal_code_from IN
                    (SELECT postal_code
                    FROM User
                    WHERE User.email= $curUserEmail)) AS D
		ON U.Postal_code = D.postal_code_to
        WHERE U.email = $itemBelongsTo
    """
    vars = {'itemBelongsTo': itemBelongsTo, 'curUserEmail': curUserEmail}

    results = dbConn.query(sql, vars=vars)
    return results

    