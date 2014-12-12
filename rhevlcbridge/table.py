'''
Created on Jan 3, 2014

@author: wallace
'''


# Define colors - yay color!
# Need more - build out later
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    SECTION = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WHITE = '\033[1;37m'
    HEADER_BOLD = '\033[95m' + '\033[1m'
    WARN = '\033[33m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    DBLUE = '\033[34m'


class Table(object):
    '''
    The Table class is meant to be call via a Database class instance.

    Ideas so far:
     - set properties
     - auto column width
    '''

    # Variables
    tableEnts = ""
    tableCols = []


    def __init__(self, entList, *args, **kwargs):
        '''
        Class should be called with:

        entList = result of get_X() function of Database object. It will be a list object, with each item being an object
        *args = these should be column names where the name of the column is the second part of a 'get_' method for the objects. (as in, get_name(), get_uuid() )
        '''
        self.tableEnts = entList  # list object will all data
        self.tableCols = []
        # print len(args)
        for a in args:
            # print "Adding \"" + a + "\""
            self.tableCols.append(a)
        # print "Arguments: " + ' '.join(self.tableCols)
        #print "Number of entities provided: " + str(len(self.tableEnts))
        #print "-------------------------------"
        #print ""
        self.validate()


    def display(self):
        # print "Display method called"

        # need to find the longest string for each column for autoformatting - up to 36 chars (size of UUID string)
        # colWidths should be a list with as many elements as there are columns specified
        colWidths = []
        for c in self.tableCols:
            # print "Finding largest width for: " + c
            methName = "get_" + c
            #print methName
            tempRange = []
            for e in self.tableEnts:
                #print e.get_name()
                # cycle through entities in a given column to find widest string under 36 chars
                widthFunc = getattr(e, methName)
                # Have to validate this in case the value returned is a boolean
                tempVal = widthFunc()
                if "bool" in str(type(tempVal)):
                    newWidth = 1
                else:
                    newWidth = len(widthFunc())
                #print "Appending " + str(newWidth) + " to range of widths."
                tempRange.append(newWidth)
            maxWidth = max(tempRange)
            #print "Found " + str(maxWidth) + " to be the largest width."
            if maxWidth <= len(c):
                #print "maxWidth was not larger than the column header, setting length to column header"
                maxWidth = len(c)
            colWidths.append(maxWidth)

        # print "Items in colWidths: " + str(len(colWidths))
        # Capitalize all column headers and
        # concatenate headers, then print
        # '=' for separators
        widthStr = ""
        contentStr = ""
        sepStr = ""
        index = 0
        #print ', '.join(self.tableCols)
        for c in self.tableCols:
            c = c.upper()
            c = c.replace("_", " ")
            #print index
            #print colWidths[index]
            #print index
            widthStr = widthStr + "{:^" + str(colWidths[index]) + "}\t"
            contentStr = contentStr + "\"" + c + "\","
            sepStr = sepStr + '=' * colWidths[index] + "\t"
            index = index + 1



        # Print the table header
        print ""
        headerStr = "\"" + widthStr.rstrip("\t") + "\".format(" + contentStr.rstrip(",") + ")"
        print "\t" + colors.WHITE + eval(headerStr)
        print "\t" + sepStr + colors.ENDC

        # Start creating and displaying data
        for e in self.tableEnts:
            linecolor = colors.BLUE
            #biggerThanHeader = False
            dataFmtStr = ""
            dataStr = ""
            entStr = ""
            index = 0
            for c in self.tableCols:
                methName = "get_" + c
                #print methName
                colFunc = getattr(e, methName)
                newVal = colFunc()
                if "bool" in str(type(newVal)):
                    if newVal:
                        newVal = "*"
                        linecolor = colors.CYAN + colors.BOLD
                    else:
                        newVal = ""
                        #linecolor = colors.CYAN
                dataStr = dataStr + "\"" + newVal + "\","
                dataFmtStr = dataFmtStr + "{:^" + str(colWidths[index]) + "}\t"
                index = index + 1

            entStr = "\"" + dataFmtStr.rstrip("\t") + "\".format(" + dataStr.rstrip(",") + ")"
            print "\t" + linecolor + eval(entStr) + colors.ENDC

        # Finishing the table
        print ""

    # print "Checking to make sure we have as many widths as we do columns (" + str(len(colWidths)) + " widths, " + str(len(self.tableCols)) + " columns)"
    # if len(colWidths) == len(self.tableCols):
    #	print "Lengths match, moving on"
    #else:
    #	print "Numbers of columns doesn't match the number of widths discovered. You've hit a problem."


    def validate(self):
        '''
        Meant to validate input during init
        '''
        # Check for valid list object
        if len(self.tableEnts) == 0:
            print "No list object for entities provided"
            return False

        # just for debugging
        elif len(self.tableEnts) > 0:
            testObj = self.tableEnts[0]
            entClass = str(testObj.__class__)
            #print "Class: " + entClass
            if "rhevlcbridge" not in entClass:
                #	print "Class passes"
                #	print "Found " + str(len(self.tableEnts)) + " entities passed to the table"
                #else:
                #	print "Class is not a valid object"
                return False

        # Check for columns, default to just name and UUID. No need to break as tableEnts has been verified to contain data, this just chooses the data to pull from
        numCols = len(self.tableCols)
        if numCols == 0:
            #print "No columns found to be passed to table, defaulting to 2: Name and UUID"
            self.tableCols = ["name", "uuid"]
        elif numCols > 0:
            testObj = self.tableEnts[0]
            #print "Found column(s) passed to table, they are: " + ','.join(self.tableCols)
            #print "Checking to ensure given entity type \"" + str(testObj.__class__) + "\" has column/methods available..."
            # grab all methods from testObj, loop through all too see if any are invalid column names (assuming column names are in the get_X())
            #print "Looping through " + str(len(self.tableCols)) + " arguments"
            objMethods = []
            for f in dir(testObj):
                objMethods.append(f)
            for c in self.tableCols:
                if c not in ' '.join(objMethods):
                    #print "Found a function that matches the column named \"" + c + "\""
                    #else:
                    #print "Nothing matched"
                    return False
            return True

    def messDEBUG(self, message):
        print colors.WARN + message





