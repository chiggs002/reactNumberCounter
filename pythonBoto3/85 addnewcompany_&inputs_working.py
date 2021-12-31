import boto3
import decimal
import random
from datetime import datetime, timedelta,date
from isoweek import Week

from boto3.dynamodb.conditions import Key, Attr

#  -----------------------------DEFINE ALL GLOBAL VARIABLES

# define the array number where we are storing today's waste date:
myN=0
checkId=''

#  WASTE STREAM TYPE (C,S,P) LENGTH OF ARRAY HELD IN DATABASE
wasteStreamArraySize=0
todayWasteStreamArraySize=0


#  SET THE ARRAY FOR THE DAYS  OF THE WEEK
set7Days = ['']*7
print("set7Days=" ,set7Days )

#  define the waste categories to auto send data out:
checkWaste = {
    'C':'coverWaste',
    'S':'spoilageWaste',
    'P':'preparationWaste'
}

#  Define the time we will add a new array slice for next time data. What hour is this done?
# newDataArrayTme = 23
# newDataArrayTme = 20
newDataArrayTme = 19

#  waste summaries for each month
sumCoverMonth =    [0,0,0,0,0,0,0,0,0,0,0,0]
sumPreparationMonth =[0,0,0,0,0,0,0,0,0,0,0,0]
sumSpoilageMonth =  [0,0,0,0,0,0,0,0,0,0,0,0]

#  set laset 30 days dates
setLast30Days = [""]*31

#  how many sites
howManySites = [0]*10
print("howManySites =",howManySites)


#  company how many sites
companyHowManySites = [0]*10
print("companyHowManySites =",companyHowManySites)
# -------------------------------------GLOBAL DATA SET ABOVE

#  total waste size
TotalWasteSize = 0

#  SET THE ARRAY FOR THE DAYS  OF THE WEEK
setCoversInput = [0]*7
print("setCoversInput" ,setCoversInput )
setEventsInput = [0]*7
print("setEventsInput=" ,setEventsInput )
setSalesInput = [0]*7
print("setCoversInput" ,setCoversInput )

#  capping array 3 items
hourlyCapping  = [ {'id':0,
                    'label':'hourlyCoverWastes',
                    'type':'C',
                    'value':0},
                   {'id':1,
                    'label':'hourlySpoilageWastes',
                    'type':'S',
                    'value':0},
                   {'id':2,
                    'label':'hourlyPreparationWastes',
                    'type':'P',
                    'value':0}
                   ]

dailyCapping  = [ {'id':0,
                   'label':'dailyCoverWastes',
                   'type':'C',
                   'value':0},
                  {'id':1,
                   'label':'dailySpoilageWastes',
                   'type':'S',
                   'value':0},
                  {'id':2,
                   'label':'dailyPreparationWastes',
                   'type':'P',
                   'value':0}
                  ]

weeklyCapping  = [ {'id':0,
                    'label':'weeklyCoverWastes',
                    'type':'C',
                    'value':0},
                   {'id':1,
                    'label':'weeklySpoilageWastes',
                    'type':'S',
                    'value':0},
                   {'id':2,
                    'label':'weeklyPreparationWastes',
                    'type':'P',
                    'value':0}
                 ]

monthlyCapping  = [ {'id':0,
                    'label':'monthlyCoverWastes',
                    'type':'C',
                    'value':0},
                    {'id':1,
                    'label':'monthlySpoilageWastes',
                    'type':'S',
                    'value':0},
                    {'id':2,
                    'label':'monthlyPreparationWastes',
                    'type':'P',
                    'value':0}
                 ]

totalCapping  = [ {'id':0,
                    'label':'totalCoverWastes',
                    'type':'C',
                    'value':0},
                    {'id':1,
                    'label':'totalSpoilageWastes',
                    'type':'S',
                    'value':0},
                    {'id':2,
                    'label':'totalPreparationWastes',
                    'type':'P',
                    'value':0}
                 ]

wastePerCoverCappingValues = [
      {
        'id': 0,
        'label': 'wastePerCoverCoverWastes',
        'type': 'C',
        'value': 1
      },
      {
        'id': 1,
        'label': 'wastePerCoverSpoilageWastes',
        'type': 'S',
        'value': 1
      },
      {
        'id': 2,
        'label': 'wastePerCoverPreparationWastes',
        'type': 'P',
        'value': 1
      }
    ]
wastePerSalesCappingValues = [
      {
        'id': 0,
        'label': 'wastePerSalesCoverWastes',
        'type': 'C',
        'value': 1
      },
      {
        'id': 1,
        'label': 'wastePerSalesSpoilageWastes',
        'type': 'S',
        'value': 1
      },
      {
        'id': 2,
        'label': 'wastePerSalesPreparationWastes',
        'type': 'P',
        'value': 1
      }
    ]

def numberOfDays(y, m):
    leap = 0
    if y % 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y % 4 == 0:
        leap = 1
    if m == 2:
        return 28 + leap
    list = [1, 3, 5, 7, 8, 10, 12]
    if m in list:
        return 31
    return 30


# menudata input
menuData= [
    {
	"menuItem":"",
	"sales":0,
	"weightPerItem":0,
	"wastePerCent":0
	},
    {
	"menuItem":"",
	"sales":0,
	"weightPerItem":0,
	"wastePerCent":0
	}
    ]

#  Production Preparation waste
#
productionPrepData = [
    {
	"productionFood":"",
    "ingredients":"",
	"totalNumber":0,
	"weightPerMeal":0,
	"totalWeight":0
	}
    ]


#  Establish the time and we want:
# datetime.today
# * myYear
# * myHour
# * myDay365
# * myDate365
print("")
print("")
print(" ..............................HOURLY ELECTRICAL DATA UPDATES.......................")
# print("")
print("")
tday = date.today()
nextYear = date.today().year + 1
print(".......nextYear=",nextYear )
print(".....................date.today()",tday)
g= datetime.today()
print(" datetime.today()=",g)
print("")
# d=datetime.date(2020,10,27)
d=date(2020,10,27)
# "%Y:%m:%d:%H:%M

myYear = g.strftime("%Y")
myMonth = g.strftime("%m")
myMonth = myMonth.lstrip("0")
# onlyfill
myHour = g.strftime("%H")
myMin  = g.strftime("%M")
myDayThisMonth =  g.strftime("%d")
myDay365 = g.strftime("%j")
nextDayNo = 1 + int(myDay365)
myDate = g.strftime("%Y-%m-%d")
nextDay = date.today()+ timedelta(days=1)

# current date: myDate, numberofweek:weekNo, dayofyear: myDay365
weekNo = str(g.strftime("%V"))
weekNo = weekNo.lstrip("0")

# newYearMonday = Week(2021,1).monday()
newThisWeekMonday = Week(int(myYear),int(weekNo)).monday()
newNextWeekMonday = Week(int(myYear),int(weekNo)+1).monday()

# d = Week(2021, 1).monday()
# newYearMonday = Week(2021,1).monday()59A addnewcompany_&items_working.py
newYearMonday = Week(nextYear,1).monday()
print ("............myyear= ",myYear )
print ("............myMonth=",myMonth )
print ("............myHour= ",myHour  )
print ("............myMin= ",myMin )
print ("............myDay365= ",myDay365 )
print ("............nextDayNo= ",nextDayNo  )
print ("............myDate= ",myDate )
print ("............NextDay= ",nextDay )
print ("....myDayThisMonth =",myDayThisMonth)
print ("...........nextYear=",nextYear)
print (".....newYearMonday =",newYearMonday)
print (".....newNextWeekMonday =",newNextWeekMonday)
print (".....newThisWeekMonday =",newThisWeekMonday)
print ("............current week number=",weekNo)


# 0-6 Monday 0  Sunday 6
print(".........day of week Monday 0  Sunday 6=", tday.weekday())
# 1-7 Monday 1 Sunday 7
print(".........day of week Monday 1  Sunday 7=",tday.isoweekday())

# Loop around the last 30 days
print ('day of the year....=',myDayThisMonth,type(myDayThisMonth))
print ("............myyear= ",myYear, "............nextYear= ",nextYear  )
print ("............myMonth=",myMonth )
daysInMonth = numberOfDays(int(myYear),int(myMonth))
print ("daysInMonth=",daysInMonth, "myDayThisMonth=",myDayThisMonth )
myMin = min(daysInMonth,int(myDayThisMonth))
print("myMin=",myMin)

# 0-6 Monday 0  Sunday 6
print(".........day of week Monday 0  Sunday 6=", tday.weekday())
# 1-7 Monday 1 Sunday 7
DayNoOfWeek = tday.isoweekday()
print(".........day of week Monday 1  Sunday 7=",DayNoOfWeek)

for i in range(7):
    # print("i=", i)
    # GO BACK TO BEGINING OF WEEK AND LOOP 7 DAYS
    set7Days[i] = str(date.today() - timedelta(days=DayNoOfWeek - 1) + timedelta(days=i))
    # set7Days[i] = str(date.today() + timedelta(days=1 + i))
    print("set7Days=", set7Days[i], '  i=', i)

#  SEARCH IN THE MASTER TABLE
masterTable = 'company_identifier_master'



# get the weight data and tel no from the electrics
# Dummy up

#  RANDOM WEIGHT
c = random.random()
c = round(c, 2)
#c = str(round(c, 2))
print("")
print("")
print("")
print("")
print("..............READING FROM DEVICE  WEIGHT DATA/TELE NUMBER:")
print("")
# print("")

# weightData = random.random()*10
weightData = c*10
weightData= str(round(weightData, 2))
# c = str(round(c, 2))

#  my telephone number

# tel="07842601123"
tel="07434629487"

print("..............weightData= ",weightData)
print("..............tel= ",tel)
print("random weight value=",c)
print("")
print("")

print()
print("")
print("")
print("SEARCHING IN DATABASE...",masterTable, "...FOR THIS TELEPHONE NO...",tel)
print("")
print("")


# key the table and get all the items at once
#  company_identifier_master
# Get the service resource.
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('company_identifier_master')
# response = table.scan()
# print("SCANNING THE TABLE.....company_identifier_master... RECEIVE ALL OF THE ITEMS (DIFF COMPANIES) WITH ATTRIBUTES")
# print("response=",response )









# Dummy Data
# newFoundCompanyData = 'True'
newFoundCompanyData = True
newAddress = "FXPlus, Penryn TR10 9FE, Cornwall"
newCompany = 'fxPlus'
newStartDate = {
    "startDate": "2021-08-07"
  }

# CARBON EMISSION VALUE DEPENDANT ON MUNICIPAL DISPOSAL METHOD
# Waste food kilo of co2 per kilo gramme:
# disposal:   Anaerobic digestion       Landfill        Incineration         Composting         Heat-moisture
# CO2.                  0.03652                         0.221.35        0.676              0.04264                   0.048.35
newCarbonMunicipalValue = 0.676

#  new municipal waste £ per tonne takeway
newMunicipalCostPerTonne = 253


# Are we getting inputs from you?
# COVER NUMBER ,,SALES NUMBER, MENU ITEMS [C,S,M]
newUserInputs = [1,1,0]


# Use the start date to push the day and week into the first item

date_time_str = newStartDate['startDate']
# date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
w = datetime.strptime(date_time_str, '%Y-%m-%d' )
print ('date_time_obj =',w )
weekNoW = w.strftime("%V")
myDay365W = w.strftime("%j")
print('weekNo =', weekNoW.lstrip("0") )
print('myDay365  =', myDay365W.lstrip("0") )

# newYearMonday = Week(2021,1).monday()
newThisWeekMondayW = Week(int(myYear),int(weekNoW)).monday()
newNextWeekMondayW = Week(int(myYear),int(weekNoW)+1).monday()
print('newThisWeekMondayW =',newThisWeekMondayW )
print('newNextWeekMondayW =',newNextWeekMondayW )




newMyDeviceID = [
    {
      "id": [
        {
          "telNo": "447434629487",
          "wasteCat": "PU",
          "unusedWaste":"P",
          "unusedTime": "14",
        }
      ],
      "opening": 8,
      "serNo": "1234567890",
      "siteId": "1_STANNARYSPECIAL"
    }
]
newEmailAddress = 'lee.hallam@fxplus.ac.uk'

newCompanyId = '1001'

newMobile =   "078421601123"

newSites =  {
    "1_STANNARYSPECIAL": [
      0,
      0,
      1
    ]
}

newUser = 'Lee Hallam'
newWorkTitle ='Director of Commercial Operations'

# Extra inputs.
newAverageSales = 1000
newAverageCover = 100

setCoversInput = [newAverageCover]*7
print("newAverageSales=" ,setCoversInput )
setSalesInput = [newAverageSales]*7
print("newAverageCover =" ,setSalesInput )



#  capping array 3 items  always in this order CSP
#  new capping on sales and covers
newWastePerCoverCappingValues = [1,1,1]
newWastePerSalesCappingValues = [1,1,1]
newHourlyCapping = [20,10,30]
newDailyCapping = [20,10,30]
newWeeklyCapping = [230,70,230]
newMonthlyCapping = [600,300,800]
newTotalCapping = [5000,3000,7000]
wastePerCoverCappingValues = [
      {
        'id': 0,
        'label': 'wastePerCoverCoverWastes',
        'type': 'C',
        'value': newWastePerCoverCappingValues[0]
      },
      {
        'id': 1,
        'label': 'wastePerCoverSpoilageWastes',
        'type': 'S',
        'value': newWastePerCoverCappingValues[1]
      },
      {
        'id': 2,
        'label': 'wastePerCoverPreparationWastes',
        'type': 'P',
        'value': newWastePerCoverCappingValues[2]
      }
    ]
wastePerSalesCappingValues = [
      {
        'id': 0,
        'label': 'wastePerSalesCoverWastes',
        'type': 'C',
        'value': newWastePerSalesCappingValues[0]
      },
      {
        'id': 1,
        'label': 'wastePerSalesSpoilageWastes',
        'type': 'S',
        'value': newWastePerSalesCappingValues[1]
      },
      {
        'id': 2,
        'label': 'wastePerSalesPreparationWastes',
        'type': 'P',
        'value': newWastePerSalesCappingValues[2]
      }
    ]

hourlyCapping  = [ {'id':0,
                    'label':'hourlyCoverWastes',
                    'type':'C',
                    'value':newHourlyCapping[0]},
                   {'id':1,
                    'label':'hourlySpoilageWastes',
                    'type':'S',
                    'value':newHourlyCapping[1]},
                   {'id':2,
                    'label':'hourlyPreparationWastes',
                    'type':'P',
                    'value':newHourlyCapping[2]}
                   ]

dailyCapping  = [ {'id':0,
                   'label':'dailyCoverWastes',
                   'type':'C',
                   'value':newDailyCapping[0]},
                  {'id':1,
                   'label':'dailySpoilageWastes',
                   'type':'S',
                   'value':newDailyCapping[1]},
                  {'id':2,
                   'label':'dailyPreparationWastes',
                   'type':'P',
                   'value':newDailyCapping[2]}
                  ]

weeklyCapping  = [ {'id':0,
                    'label':'weeklyCoverWastes',
                    'type':'C',
                    'value':newWeeklyCapping[0]},
                   {'id':1,
                    'label':'weeklySpoilageWastes',
                    'type':'S',
                    'value':newWeeklyCapping[1]},
                   {'id':2,
                    'label':'weeklyPreparationWastes',
                    'type':'P',
                    'value':newWeeklyCapping[2]}
                 ]

monthlyCapping  = [ {'id':0,
                    'label':'monthlyCoverWastes',
                    'type':'C',
                    'value':newMonthlyCapping[0]},
                    {'id':1,
                    'label':'monthlySpoilageWastes',
                    'type':'S',
                    'value':newMonthlyCapping[1]},
                    {'id':2,
                    'label':'monthlyPreparationWastes',
                    'type':'P',
                    'value':newMonthlyCapping[2]}
                 ]

totalCapping  = [ {'id':0,
                    'label':'totalCoverWastes',
                    'type':'C',
                    'value':newTotalCapping[0]},
                    {'id':1,
                    'label':'totalSpoilageWastes',
                    'type':'S',
                    'value':newTotalCapping[1]},
                    {'id':2,
                    'label':'totalPreparationWastes',
                    'type':'P',
                    'value':newTotalCapping[2]}
                 ]


#  Create a new company item
#   CAREFUL WITH THE MONDAY YOU CHOOSE :  EITHER str(newYearMonday)   OR str(newWeekMonday)
# eval(newFoundCompanyData)
if (newFoundCompanyData == True):
    print("NEW COMPANY:", newCompany, "found new company data:", newFoundCompanyData)
    print("********************    CREATE COMPANY DATA    ***********************")
    print("********************   PUSH ITEM  :",newCompany,"      ***********************")
    print("********************   PUSH ITEM  :",newCompany, "      ***********************")

    # table = dynamodb.Table(accessAllTables) decimal.Decimal(weightData)

    table.put_item(
        Item={
            'address': newAddress,
            'company': newCompany,
            'date': newStartDate,
            'deviceID': newMyDeviceID,
            'emailAddress': newEmailAddress,
            'id': newCompanyId,
            'mobileNumber':newMobile,
            'sites': newSites,
            'user': newUser,
            'workTitle':newWorkTitle,
            'CarbonMunicipalValue': str(newCarbonMunicipalValue),
            'municipalCostPerTonne': str(newMunicipalCostPerTonne),
            "inputsFromUser":
                {
                    "coverInputData": newUserInputs[0],
                    "salesInputData": newUserInputs[1],
                    "menuInputData": newUserInputs[2]
                }
        }

    )
print()
print()


print("******************        create a new company table       *************")

# Create the DynamoDB table
# newCompanyId = '1001'
# newCompany='fxPlus'

newCompanyAllReports = newCompanyId +'_'+ newCompany +'_allReports'




print()
print()
print()
print('Create new TABLE company allReports =',newCompanyAllReports)
print()
print()
# .Table name	                              users
# Primary partition key	                      username (String)            HASH
# Primary1 create_table_book_1.py sort key	                          last_name (String)           RANGE (edited)
try:
    table = dynamodb.create_table(
        TableName=newCompanyAllReports,
        KeySchema=[
            {
                'AttributeName': 'site',
                'KeyType': 'HASH'
            }
            # {
            #     'AttributeName': 'last_name',
            #     'KeyType': 'RANGE'
            # }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'site',
                'AttributeType': 'S'
            },
            # {
            #     'AttributeName': 'last_name',
            #     'AttributeType': 'S'
            # },
        ],
        BillingMode='PAY_PER_REQUEST'
        # ProvisionedThroughput={
        #     'ReadCapacityUnits': 1,
        #     'WriteCapacityUnits': 1
        # }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=newCompanyAllReports)

    # Print out some data about the table.
    print(table.item_count)

    # print out all items
    print(table)
    print("The table....", newCompanyAllReports, "  has been created")
    print(" --------------> we finished making Table:",newCompanyAllReports)
    print(" --------------> we finished making Table:", newCompanyAllReports)
    print(" --------------> we finished making Table:", newCompanyAllReports)
except:
    print("---------------->      Table already exists:", newCompanyAllReports)
    print("---------------->      Table already exists:", newCompanyAllReports)
    print("---------------->      Table already exists:", newCompanyAllReports)




#  NOW GET THE COMPANY DATA YOU SET UP

# table = dynamodb.Table('company_identifier_master')
#
# #  KeyConditionExpression=Key('site').eq('1_STANNARY_dailyElectricalData_2020')
# response = table.query(
#     # only the primary key
#     KeyConditionExpression=Key('company').eq(newCompany)
#     # KeyConditionExpression = Key('site').eq('1_STANNARY_dailyElectricalData_2020')
# )
#
# # response = table.scan()
# # print("RESPONSE=",response)
# items = response['Items']
# print("ITEMS===========", items)
#
#
#


# newFoundCompanyData = True
# newAddress = "FXPlus, Penryn TR10 9FE, Cornwall"
# newCompany = 'fxPlus'
# newStartDate = {
#     "startDate": "2021-06-21"
#   }
# newMyDeviceID = [
#     {
#       "id": [
#         {
#           "telNo": "078421601123",
#           "wasteCat": "P"
#         },
#       ],
#       "opening": 8,
#       "serNo": "1234567890",
#       "siteId": "1_STANNARYSPECIAL"
#     }
# ]
# newEmailAddress = 'lee.hallam@fxplus.ac.uk'
#
# newCompanyId = '1001'
#
# newMobile =   "078421601123"
#
# newSites =  {
#     "1_STANNARYSPECIAL": [
#       0,
#       0,
#       1
#     ]
# }
#
# newUser = 'Lee Hallam'
# newWorkTitle ='Director of Commercial Operations'




#  LOOPING ALL COMPANY SITES
#  LOOPING ALL COMPANY SITES
# 'SET hourlyWaste.coverWaste['+str(index)+']
# print
print("INSIDE ONE COMPANY:")
print("COMPANY NAME ID:",newCompany)
company = newCompany
id = newCompanyId
sites = newSites
sitesNumber =len(newMyDeviceID)
print("SITES FOUND:....",len(newMyDeviceID))

# for count, values in enumerate(range(num)):
for count,j in enumerate(newMyDeviceID):
    print("company=",company,'siteId=',j['siteId'])
    howManySites[count] = {
        "coverWaste": 0,
        "preparationWaste": 0,
        "spoilageWaste": 0,
        'siteName': j['siteId'],
        'trend': {
            'sumTrendCover': 0,
            'sumTrendPrep': 0,
            'sumTrendSpoil': 0
        }
    }

allSitesInput = list(filter(lambda a: a != 0, howManySites))
print("")
print("allSitesInput =", allSitesInput)
print("")
print("")
#  LOOPING ALL SITES OF 1 COMPANY
#  LOOPING ALL SITES OF 1 COMPANY
#  LOOPING ALL SITES OF 1 COMPANY
#  LOOPING ALL COMPANY SITES FOR EACH COMPANY AND EACH SITE
#  SCAN THRU DICTIONARY ITEMS OF COMPANY MASTER TABLE;
for meItems in newMyDeviceID:
    #  waste summaries for each month
    #
    # print(meitems['telNo']) search for my tel no
    # {
    #     "serNo": "123456789012345",
    #     "siteId": "1_STANNARY",
    #     "telNo": "07842601123",
    #     "wasteCat": "C"
    # # },
    n = 0

    #  SCAN IN SIDE  'deviceID' for all the sites!!!!!!!
    if (meItems["siteId"] ):
        siteId = meItems['siteId']
        # wasteCat = meItems['wasteCat']
        mycode = sites[siteId]
        myid = id
        mycompany = company
        we_found_tel = True
        openingTime = meItems['opening']
        mycode = sites[siteId]
        myid = id
        mycompany = company
        we_found_tel = True
        openingHours = [0] * int(openingTime + 1)
        # ONE YEAR ONLY OF ELECTRICAL DATA
        hourlyDataThisYear = siteId + '_' + 'dailyElectricalData' + '_' + myYear
        monthlyDateDataThisYear = siteId + '_' + 'monthlyWaste' + '_' + myYear
        weeklyDateDataThisYear = siteId + '_' + 'weeklyWaste' + '_' + myYear

        # new items weeklyCoversInput
        weeklyAIPredictionsThisYear = siteId + '_' + 'aiPrediction' + '_' + myYear
        weeklyCoversInputThisYear = siteId + '_' + 'weeklyCoversInput' + '_' + myYear
        weeklySalesInputThisYear = siteId + '_' + 'weeklySalesInput' + '_' + myYear
        weeklyAllSitesThisYear =  'allSites' + '_' + myYear
        sitesUsersLoginTimeThisYear = "sites_usersLoginTime"
        sitesweeklyDateWasteThisYear = "sites_weeklyDateWaste"
        sitesRecommendedTargetsThisYear = siteId +  '_' +  'recommendedTargets'
        sitesCappingValuesThisYear = siteId +  '_' +  'capping'
        weeklyMenuInputThisYear = siteId + '_' + 'menuInput' + '_' + myYear
        weeklyGreenSavingsThisYear = siteId + '_' + 'greenSavings' + '_' + myYear
        weeklyProductionPrepThisYear = siteId + '_' + 'productionPreparation' + '_' + myYear

      

        # ********************************** LOOP DAILY ELECTRICAL DATA



        # DayNoOfWeek = tday.isoweekday()
        print(".........day of week Monday 1  Sunday 7=", DayNoOfWeek)



        # electrical data start to fill from first monday of date
        newElectricalDataArray = []


        for i in range(DayNoOfWeek ):
            # print("i=", i)
            # GO BACK TO BEGINING OF WEEK AND LOOP 7 DAYS
            newElectricalData = {
                "dayOfYear": str(int(myDay365)-(int(DayNoOfWeek) - 1)+i),
                "coverWaste": openingHours,
                "preparationWaste": openingHours,
                "spoilageWaste": openingHours,
                "Date": str(date.today() - timedelta(days=DayNoOfWeek - 1) + timedelta(days=i))
            }
            # set7Days[i] = str(date.today() - timedelta(days=DayNoOfWeek - 1) + timedelta(days=i))

            print("newElectricalData =", newElectricalData, '  i=', i)
            newElectricalDataArray.append(newElectricalData)

        # ********************************** LOOP DAILY ELECTRICAL DATA







        # wasteType = checkWaste[wasteCat]

        print()
        print()
        print()

        print()
        print("*****************    ACCESSING NEW SITE      *****************************",siteId)
        print("*****************    ACCESSING NEW SITE      *****************************",siteId)
        print("*****************    ACCESSING NEW SITE      *****************************",siteId)

        # errorList = "200:yesFound: " + tel
        # print(errorList)

        # print("PARAMETER LIST: ", company)
        print("  siteId=", siteId,"  myid=", myid)
        # print("wastecat=", wasteCat)
        # print(" company=", company)
        # print("      id=", id)
        # print("  mycode=", mycode)

        #  FOR EACH SITEID ACCESS ALL OF THEIR ITEMS
        #  FOR EACH SITEID ACCESS ALL OF THEIR ITEMS
        #  FOR EACH SITEID ACCESS ALL OF THEIR ITEMS
        #  How do we access the tables?  {id}_{company}_allReports
        accessAllTables = id + '_' + company + '_' + 'allReports'

        # accessAllTables = '1001' + '_' + company + '_' + 'allReports'
        print("  ACCESS ALL THE COMPANY REPORTS OF THE TABLE....=", accessAllTables)
        # print("")
        # sumCoverMonth = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        # sumPreperationMonth = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        # sumSpoilageMonth = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

        #  ONLY ACCESS DIFFRENT TABLES FOR DIFFERENT COMPANY SITES
        print("  CHECKID VALUE:", checkId,"ID:",id)
        if ( id != checkId):
            table = dynamodb.Table(accessAllTables)
            checkId = id
            print("  CHECKID CHANGED:",checkId)

        #  FOR EACH SITEID
        print("  SCAN ALL OF THE ITEMS IN THE TABLE:",accessAllTables)

        print("  id_ company _allReports")
        print("  siteId _dailyElectricalData _year")
        print("  siteId _weeklyDateWaste")
        print("  siteId _monthlyWaste")
        print("  allSites")

        #PRINT ALL ITEMS OF A TABLE
        response = table.scan()
        print('Table Response=',response)
        # print(response['Items'] ['dayoOfTheYear'])
        #
        #  FOR EACH SITEID:
        # print("SCANNING THIS TABLE:", accessAllTables, "........No of items in table:", len(response['Items']))
        #  FOR EACH SITE LOOK FOR ELECTRICAL DATA ( WE ARE DOING THI FOR EVRY SITE FOR VERY COMPANY)

        #  SET ALL NEXT YEAR FLAGS TO FALSE UNTIL WE FIND THEM
        #  weeklyCoversInputNextYear = siteId + '_' + 'weeklyCoversInput' + '_' + str(nextYear)
        #             weeklySalesInputThisYear = siteId + '_' + 'weeklySalesInput' + '_' + str(nextYear)
        #             weeklyAllSitesThisYear = 'allSites' + '_' + str(nextYear)


        # found_NextYear = False
        # found_NextYear = False
        # found_NextYear = False

        found_dataThisYear = False
        found_weeklyThisYear = False
        found_monthlyThisYear = False
        found_monthlyThisYear = False
        found_aipredictionThisYear = False
        found_allSitesThisYear = False
        found_weeklyCoversInputThisYear = False
        found_weeklySalesInputThisYear = False
        found_weeklyGreenSavingsInputThisYear = False

        #  not mormally used
        found_sitesUsersLoginTimeThisYear = False
        found_sitesweeklyDateWasteThisYear = False
        found_cappingValuesThisYear = False
        found_recommendedTargetsThisYear = False
        found_weeklyMenuInputThisYear = False
        found_productionPrepWasteThisYear = False




        # weeklyAIPredictionsThisYear = siteId + '_' + 'aiPrediction' + '_' + myYear
        # weeklyCoversInputThisYear = siteId + '_' + 'weeklyCoversInput' + '_' + myYear
        # weeklySalesInputThisYear = siteId + '_' + 'weeklySalesInput' + '_' + myYear
        # weeklyAllSitesThisYear = 'allSites' + '_' + myYear

        print("  found_dataThisYear=",found_dataThisYear )
        print("  found_weeklyThisYear=", found_weeklyThisYear)
        print("  found_monthlyThisYear=",found_monthlyThisYear)
        print()
        print()
        # for meItems in response['Items']:
        #     print("ALL THE SITES IN THIS TABLE:",meItems['site'] )


        for meItems in response['Items']:
            # INSIDE A COMPANY SCANNING ALL ITEMS:
            print ( "----------------        INSIDE A COMPANY SCANNING ALL ITEMS:",meItems['site'])

            #  CHECK NEXT YEAR ITEMS
            print("---------------- CHECKING NEXT YEAR ITEMS-----------")




            #   weeklyAIPredictionsNextYear = siteId + '_' + 'aiPrediction' + '_' + str(nextYear)
            #             weeklyCoversInputNextYear = siteId + '_' + 'weeklyCoversInput' + '_' + str(nextYear)
            #             weeklySalesInputNextYear = siteId + '_' + 'weeklySalesInput' + '_' + str(nextYear)
            #             weeklyAllSitesNextYear = 'allSites' + '_' + str(nextYear)
            #  CHECK THIS YEAR ITEMS
            print("---------------- CHECKING THIS YEAR ITEMS-----------")


            if (meItems['site'] == hourlyDataThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS ELECTRICAL DATA:", hourlyDataThisYear)
                found_dataThisYear = True

                    # found_dataNextYear = False
                     # found_monthlyNextYear = False


            if (meItems['site'] == weeklyDateDataThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS WEEKLY DATA:", weeklyDateDataThisYear)
                found_weeklyThisYear = True

            if meItems['site'] == monthlyDateDataThisYear:
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS MONTHLY DATA:", monthlyDateDataThisYear)
                found_monthlyThisYear = True

            if (meItems['site'] == weeklyAllSitesThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND this YEARS allsites DATA:", weeklyAllSitesThisYear)
                found_allSitesThisYear = True

            if (meItems['site'] == weeklyAIPredictionsThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS AI PREDICTION DATA:", weeklyAIPredictionsThisYear)
                found_aipredictionThisYear = True

            if (meItems['site'] == weeklyCoversInputThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS covers input DATA:", weeklyCoversInputThisYear)
                found_weeklyCoversInputThisYear = True

            if (meItems['site'] == weeklySalesInputThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS SALES input DATA:", weeklySalesInputThisYear)
                found_weeklySalesInputThisYear = True

            if (meItems['site'] == weeklyGreenSavingsThisYear ):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS GREEN SAVINGS DATA:", weeklyGreenSavingsThisYear)
                found_weeklyGreenSavingsInputThisYear = True

            if (meItems['site'] == weeklyProductionPrepThisYear ):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS PREPARATION PRODUCTION DATA:",weeklyProductionPrepThisYear)

                found_productionPrepWasteThisYear = True
            

            #  MISSING THESE ITEMS :
            # • sites_weeklyDateWaste
            # • sites_usersLoginTime

            if (meItems['site'] == sitesRecommendedTargetsThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND next YEARS  sitesRecommendedTargetsThisYea :", sitesRecommendedTargetsThisYear)
                found_recommendedTargetsThisYear = True

            if (meItems['site'] == sitesCappingValuesThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND next YEARS  sitesCappingValuesNextYear :", sitesCappingValuesThisYear)
                found_cappingValuesThisYear = True


            if (meItems['site'] == sitesUsersLoginTimeThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS  UsersLoginTimeThisYear:", sitesUsersLoginTimeThisYear)
                found_sitesUsersLoginTimeThisYear = True

            if (meItems['site'] == sitesweeklyDateWasteThisYear):
                #  todays date and next dayprint("")
                print(" WE FOUND THIS YEARS WEEKLY DATES MON-TO-SUN Input:", sitesweeklyDateWasteThisYear)
                found_sitesweeklyDateWasteThisYear = True

            if (meItems['site'] == weeklyMenuInputThisYear):
                #  todays date and next dayprint("")
                print(" **************        WE FOUND THIS YEARS MENU INPUT DATA:", weeklyMenuInputThisYear)
                found_weeklyMenuInputThisYear = True

        n= n +1
        print("N VALUE OF deviceID :   n= ", n)
        print()
        print()
        print("COMPANY NAME:",mycompany)
        print("SITE:", siteId, "ELECTRICAL DATA : THIS YEAR:",myYear,found_dataThisYear)
        print("SITE:", siteId, "MONTHLY DATA : THIS YEAR:", myYear,found_monthlyThisYear)
        print()
        print()
        print("CAREFUL WITH THE MONDAY YOU CHOOSE :  EITHER ",str(newYearMonday) ,"OR", str(newThisWeekMonday))
        print("CAREFUL WITH THE MONDAY YOU CHOOSE :  EITHER ", str(newYearMonday), "OR", str(newThisWeekMonday))
        print("CAREFUL WITH THE MONDAY YOU CHOOSE :  EITHER ", str(newYearMonday), "OR", str(newThisWeekMonday))
        print()
        print()
        print()
        print()
        # if (found_dataNextYear==False):")

        # # current date: myDate, numberofweek:weekNo, dayofyear: myDay365
        # newThisWeekMondayW = Week(int(myYear),int(weekNoW)).monday()
        # newNextWeekMondayW = Week(int(myYear),int(weekNoW)+1).monday()

        #   CAREFUL WITH THE MONDAY YOU CHOOSE :  EITHER str(newYearMonday)   OR str(newWeekMonday)
        if (found_dataThisYear==False):
            print("SITE:", siteId,"ELECTRICAL DATA : THIS YEAR:",myYear,found_dataThisYear)
            print("********************    CREATE NEXT YEAR ELECTRICAL ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT YEAR ELECTRICAL ITEM  ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT YEAR ELECTRICAL ITEM  ***********************")
            # table = dynamodb.Table(accessAllTables)

            table.put_item(
                Item={
                    'dayOfTheYear':
                        newElectricalDataArray,
                    'siteName':siteId,
                    'site':hourlyDataThisYear
                }

            )
        print()
        print()
        # sumCoverMonth =    [0,0,0,0,0,0,0,0,0,0,0,0]
        # sumPreparationMonth =[0,0,0,0,0,0,0,0,0,0,0,0]
        # sumSpoilageMonth =  [0,0,0,0,0,0,0,0,0,0,0,0]
        if (found_weeklyThisYear==False):
            print("SITE:", siteId,"WEEKLY  DATA : THIS YEAR:",myYear,found_weeklyThisYear)
            print("********************    CREATE NEXT YEAR WEEKLY DATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT YEAR WEEKLY DATA  ITEM   ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT YEAR WEEKLY DATA  ITEM   ***********************")
            # table = dynamodb.Table(accessAllTables)

            table.put_item(
                Item={
                    'weeklyWasteSum':
                        [{
                            "Date": str(newThisWeekMonday),
                            "coverWaste": [0],
                            "preparationWaste": [0],
                            "spoilageWaste": [0],
                            "weekOfYear": str(weekNo)
                        }],
                    'siteName':siteId,
                    'site': weeklyDateDataThisYear
                }

            )
        # "Date": str(nextDay),
        if (found_monthlyThisYear==False):
            print("monthlyDateDataNextYear=", monthlyDateDataThisYear)
            print("SITE:", siteId,"MONTHLY DATA :THIS YEAR:",myYear,found_monthlyThisYear)
            print("********************    CREATE NEXT YEAR MONTHLY DATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT YEAR MONTHLY DATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT YEAR MONTHLY DATA  ITEM    ***********************")
            table.put_item(
                Item={
                    'monthlyValue': {
                        'monthly': {
                            "coverWaste": sumCoverMonth,
                            "preparationWaste": sumPreparationMonth,
                            "spoilageWaste": sumSpoilageMonth,
                        },
                        'siteName': siteId
                    },
                    'site': monthlyDateDataThisYear

                }
            )
#         found_allSitesNextYear = False
#             found_aipredictionNextYear = False
#             found_weeklyCoversInputNextYear = False
#             found_weeklySalesInputTNextYear = False
#         weeklyAIPredictionsNextYear = siteId + '_' + 'aiPrediction' + '_' + str(nextYear)
        #             weeklyCoversInputNextYear = siteId + '_' + 'weeklyCoversInput' + '_' + str(nextYear)
        #             weeklySalesInputNextYear = siteId + '_' + 'weeklySalesInput' + '_' + str(nextYear)
        #             weeklyAllSitesNextYear = 'allSites' + '_' + str(nextYear)
        # eeklyGreenSavingsThisYear


        if (found_weeklyGreenSavingsInputThisYear == False):
            print("weeklyGreenSavingsThisYear=", weeklyGreenSavingsThisYear)
            print("SITE:", siteId, "weekly saLES input THIS YEAR:",myYear,found_weeklyGreenSavingsInputThisYear)
            print("********************    CREATE NEXT years  sales input   ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years  sales input    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years  sales input    ***********************")
            table.put_item(
                Item={
                    'weeklyWaste': [{
                        "weekOfYear": str(weekNo),
                        "allWaste": [],
                        "Date": str(newThisWeekMonday)

                    }],
                    'siteName': siteId,
                    'site': weeklyGreenSavingsThisYear

                }
            )




        if (found_weeklySalesInputThisYear == False):
            print("weeklySalesInputNextYear=", weeklySalesInputThisYear)
            print("SITE:", siteId, "weekly saLES input THIS YEAR:",myYear,found_weeklySalesInputThisYear)
            print("********************    CREATE NEXT years  sales input   ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years  sales input    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years  sales input    ***********************")
            table.put_item(
                Item={
                    'weeklySales': [{
                        "weekOfYear": str(weekNo),
                        "salesInput": setSalesInput,
                        "Date": str(newThisWeekMonday)

                    }],
                    'siteName': siteId,
                    'site': weeklySalesInputThisYear

                }
            )


        if (found_weeklyCoversInputThisYear == False):
            print("weeklyCoversInputNextYear=", weeklyCoversInputThisYear)
            print("SITE:", siteId, "weekly cover input : THIS YEAR:",myYear,found_weeklyCoversInputThisYear )
            print("********************   PUSH ITEM  :    CREATE NEXT years weekly cover input    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years weekly cover input    ***********************")


            table.put_item(
                Item={
                    'weeklyCovers': [{
                        "weekOfYear": str(weekNo),
                        "checkBox": setEventsInput,
                        "coversInput": setCoversInput,
                        "Date":str(newThisWeekMonday)

                    }],
                    'siteName': siteId,
                    'site': weeklyCoversInputThisYear

                }
            )


        if (found_aipredictionThisYear==False):
            print("weeklyAIPredictionsNextYear=", weeklyAIPredictionsThisYear)
            print("SITE:", siteId,"AI PREDICTION DATA : THIS YEAR:",myYear,found_aipredictionThisYear)
            print("********************    CREATE NEXT YEAR AI PREDICTION  DATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years AI PREDICTION  DATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years AI PREDICTION  DATA  ITEM    ***********************")
            table.put_item(
                Item={
                    'aiPrediction': {
                        'siteName': siteId,
                        'dailyForcastsBasedOnCurrentMonth': {
                            'coverWaste':0,
                            'preparationWaste': 0,
                            'spoilageWaste': 0,
                        },
                        'weeklylyForcastsBasedOnCurrentMonth': {
                            'coverWaste': 0,
                            'preparationWaste': 0,
                            'spoilageWaste': 0,
                        },
                        'monthlyForcastsBasedOnCurrentMonth': {
                            'coverWaste': 0,
                            'preparationWaste': 0,
                            'spoilageWaste': 0,
                        },
                        'yearlyForcastsBasedOnCurrentMonth': {
                            'coverWaste': 0,
                            'preparationWaste': 0,
                            'spoilageWaste': 0,
                        },

                    },
                    'site': weeklyAIPredictionsThisYear
                }
            )


        if (found_allSitesThisYear==False):
            print("allSitesNextYearr=", weeklyAllSitesThisYear)
            print("SITE:", siteId,"ALLSITES DATA :: THIS YEAR:",myYear,found_allSitesThisYear)
            print("********************    CREATE NEXT YEAR   ALLSITESDATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years ALLSITESDATA  ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years ALLSITESDATA  ITEM    ***********************")
            table.put_item(
                Item={
                    'totalWaste': {
                        'sites': allSitesInput,

                    },
                    'site': weeklyAllSitesThisYear

                }
            )


        # DONT USE THIS IN THE ANNUAL CODE
        # DONT USE THIS IN THE ANNUAL CODE
        # DONT USE THIS IN THE ANNUAL CODE
        # DONT USE THIS IN THE ANNUAL CODE
        # found_sitesUsersLoginTimeNextYear = False
        # found_sitesweeklyDateWasteNextYear = False
        # sitesUsersLoginTimeNextYear = "sites_usersLoginTime" + '_' + str(nextYear)
        # sitesweeklyDateWasteNextYear = "sites_weeklyDateWaste" + '_' + str(nextYear)

        #   sitesUsersLoginTimeThisYear = "sites_usersLoginTime"
        #    sitesweeklyDateWasteThisYear= "sites_weeklyDateWaste"
        if (found_sitesUsersLoginTimeThisYear==False):
            print("UsersLoginNextYearr=",sitesUsersLoginTimeThisYear)
            print("SITE:", siteId,"UsersLogin : : THIS YEAR:",myYear,found_sitesUsersLoginTimeThisYear)
            print("********************    CREATE NEXT YEAR   UsersLogin ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years UsersLogin ITEM    ***********************")
            print("********************   PUSH ITEM  :    CREATE NEXT years UsersLogin ITEM    ***********************")
            table.put_item(
                Item={
                    'superAdminCreatedUsers':[{
                    'name':'contact',
                    'username':'contact@greenkode.net',
                    'loginTime': [{'time':'Dummy'}]
                    }],
                    'site': sitesUsersLoginTimeThisYear
                }
            )

        if (found_sitesweeklyDateWasteThisYear==False):
            print("sitesweeklyDateWasteNextYear=",sitesweeklyDateWasteThisYear)
            print("SITE:", siteId,"UsersLogin : : THIS YEAR:",myYear,found_sitesweeklyDateWasteThisYear)
            print("********************    CREATE NEXT YEAR   sitesweeklyDateWasteNextYear ITEM    ***********************")
            print("********************   PUSH ITEM :CREATE NEXT years  ITEM    ***********************")
            print("********************   PUSH ITEM : CREATE NEXT years sitesweeklyDateWasteNextYear ITEM    ***********************")
            table.put_item(
                Item={
                    'weeklyDates': set7Days,
                    'site': sitesweeklyDateWasteThisYear
                }
            )
        #             found_cappingValuesNextYear = False
        #             found_recommendedTargetsNextYear = False
        # sitesRecommendedTargetsNextYear = siteId + + '_' +  'recommendedTargets' + '_' + str(nextYear)
        #             sitesCappingValuesNextYear = siteId + '_' + 'capping'+ '_' + str(nextYear)
        if (found_recommendedTargetsThisYear==False):
            print("sitesRecommendedTargetsNextYear=",sitesRecommendedTargetsThisYear)
            print("SITE:", siteId,"UsersLogin : : THIS YEAR:",myYear,found_recommendedTargetsThisYear)
            print("********************    CREATE NEXT YEAR   RecommendedTargetsNextYear   ***********************")
            print("********************   PUSH ITEM :CREATE NEXT years  ITEM    ***********************")
            print("********************   PUSH ITEM : CREATE NEXT years RecommendedTargetsNextYear ITEM    ***********************")
            table.put_item(
                Item={
                    'recommendedTargets': {
                        'companyId': id,
                        'companyname': company,
                        'siteID': siteId,
                        'targets': {
                            'coverBreakDown': 0,
                            'percents': "10",
                            'percentSavingsInAday': 0,
                            'percentSavingsInAmonth': 0,
                            'percentSavingsInAweek': 0,
                            'percentSavingsInAyear': 0,
                            'prepBreakDown': 0,
                            'recommendTarget': 0,
                            'spoilageBreakDown': 0,
                            'totalCSPforPreviousMonth': 0,
                            'totalPercentagedSavingsTotal': 0,
                            'yearlyKilosOfCO2saved': 0,
                            'yearlyMealsSaved': 0
                        }
                    },
                    'site': sitesRecommendedTargetsThisYear
                }
            )

        if (found_cappingValuesThisYear ==False):
            print("sitesCappingValuesNextYear =",sitesCappingValuesThisYear)
            print("SITE:", siteId,"UsersLogin : THIS YEAR:",myYear,found_cappingValuesThisYear)
            print("********************    CREATE NEXT YEAR   sitesCappingValuesNextYear ITEM    ***********************")
            print("********************   PUSH ITEM :CREATE NEXT years  ITEM    ***********************")
            print("********************   PUSH ITEM : CREATE NEXT years sitesCappingValuesNextYear ITEM    ***********************")
            table.put_item(
                Item={
                    'cappingValue': {
                        'companyId': id,
                        'companyName': company,
                        'siteId': siteId,
                        'dailyCappingValues':dailyCapping,
                        'hourlyCappingValues': hourlyCapping,
                        'weeklyCappingValues': weeklyCapping,
                        'monthlyCappingValues': monthlyCapping,
                        'totalCappingValues': totalCapping,
                        'wastePerCoverCappingValues':wastePerCoverCappingValues,
                        'wastePerSalesCappingValues': wastePerSalesCappingValues
                    },
                    'site': sitesCappingValuesThisYear
                }
            )

        #   weeklyMenuInputThisYear = siteId + '_' + 'menuInput' + '_' + myYear
        if (found_weeklyMenuInputThisYear == False):
            print("weeklyMenuInputNextYear=", weeklyMenuInputThisYear)
            print("SITE:", siteId, "UsersLogin : NEXT YEAR:", nextYear, found_weeklyMenuInputThisYear)
            print(
                "********************    CREATE NEXT YEAR   weeklyMenuInputNextYearITEM    ***********************")
            print("********************   PUSH ITEM :CREATE NEXT years  ITEM    ***********************")
            print(
                "********************   PUSH ITEM : CREATE NEXT years weeklyMenuInputNextYear ITEM    ***********************")
            table.put_item(
                Item={
                    'menuWaste': [{
                        "weekOfYear": str(weekNo),
                        "Date": str(newThisWeekMonday),
                        "menuWasteWeek":
                            [menuData, menuData, menuData, menuData, menuData, menuData, menuData],
                    }],
                    'siteName': siteId,
                    'site': weeklyMenuInputThisYear

                }
            )

        # weeklyProductionPrepNextYear = siteId + '_' + 'productionPreparation' + '_' + str(nextYear)
        # greenSavingsNextyear = siteId + '_' + 'greenSavings' + '_' + str(nextYear)
        #             found_greenSavingsNextYear = False
        #             found_productionPrepWasteNextYear = False
        # #      UpdateExpression='SET productionPreparation[' + str(whatWeek) + ']=:r',
        #     ExpressionAttributeValues={
        #         ':r':  {
        #                 "weekOfYear": str(weekNo),
        #                 "Date": str(newWeekMonday),
        #                 "productionWasteWeek":
        #                     [productionPrepData, productionPrepData, productionPrepData, productionPrepData, productionPrepData, productionPrepData,productionPrepData]
        #             }
        #     }
        # found_greenSavingsThisYear = False
        # found_productionPrepWasteThisYear = False
        print("")
        print("found_productionPrepWasteThisYear =",found_productionPrepWasteThisYear)
        print("")
        if (found_productionPrepWasteThisYear == False):
            print("weeklyProductionPrepThisYear=", weeklyProductionPrepThisYear)
            print("SITE:", siteId, "UsersLogin : NEXT YEAR:", nextYear,)
            print(
                "********************    CREATE NEXT YEAR productionPreparation  ITEM    ***********************")
            print("********************   PUSH ITEM :CREATE NEXT years  ITEM    ***********************")
            print(
                "********************   PUSH ITEM : CREATE NEXT years PRODUCTION PREPARATION WASTE ITEM    ***********************")
            table.put_item(
                Item={
                    'productionPreparation': [{
                        "weekOfYear": str(weekNo),
                        "Date": str(newThisWeekMonday),
                        "productionWasteWeek":
                            [productionPrepData, productionPrepData, productionPrepData, productionPrepData,
                             productionPrepData, productionPrepData, productionPrepData]
                        ,
                    }],
                    'siteName': siteId,
                    'site': weeklyProductionPrepThisYear

                }
            )
print()

print("******************       new company  UPDATES COMPLETED       *************")

