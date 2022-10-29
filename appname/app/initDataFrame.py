from bs4 import BeautifulSoup
import pandas as pd


def create_df(path, category):
    d={'HYPERLINK':[], #attributes, landx,landy,photourl
       'DESCRIPTION': [],
       'ADDRESSUNITNUMBER': [],
       'ADDRESSSTREETNAME': [],
       'ADDRESSPOSTALCODE': [],
       'ADDRESSFLOORNUMBER': [],
       'ADDRESSBUILDINGNAME': [],
       'ADDRESSBLOCKHOUSENUMBER': [], #inc_crc, fmel_upd_d
       'NAME': []}
    keys = list(d.keys())

    with open(path) as data:
        kml_soup = BeautifulSoup(data, 'lxml-xml') # Parse as XML

    descriptions = kml_soup.find_all('description')
    for description in descriptions:
        html_soup = BeautifulSoup(description.text, 'lxml') # Parse as HTML
        tables = html_soup.find_all('table')
        # print(len(tables))
        for table in tables:
            rows = table.find_all('tr')
            count=0
            # print("rows", rows)
            for row in rows:
                # print("curr row",row)
                # row_names = table.find_all('th')
                # print("row_name", row_names)
                if count==0 or count==1 or count==2 or count==3 or count==12 or count==13:
                    count +=1
                    continue
                cols = row.find_all('td')
                cols = str(cols).replace('[<td>', '')
                cols = cols.replace('</td>]', '')
                # if cols == '':
                #     print("none")
                if count == 14:
                    d[keys[count-6]].append(cols)
                else:
                    d[keys[count - 4]].append(cols)

                count+=1
                # print("cols", cols)
                # print(d)
                # for v in d.values():
                #     print(len(v))

    df = pd.DataFrame(d)
    # print(df.to_string())
    coord_count = 0
    latitude = []
    longitude = []
    for coords in kml_soup.find_all('coordinates'):

                # Take coordinate string from KML and break it up into [Lat,Lon,Lat,Lon...] to get CSV row
                space_splits = coords.string.split(" ")
                #print(space_splits)


                for split in space_splits:
                    # Note: because of the space between <coordinates>" "-80.123, we slice [1:]
                    comma_split = split.split(',')
                    # lattitude
                    latitude.append(comma_split[1])
                    # df.iloc[coord_count]["latitude"] = comma_split[1]

                    # longitude
                    longitude.append(comma_split[0])
                    # df.iloc[coord_count]["longitude"] = comma_split[0]
                    coord_count +=1

    # print(len(latitude))
    # print(len(longitude))
    df['LATITUDE'] = latitude
    df['LONGITUDE'] = longitude
    df['CATEGORY'] = category
    # print(df.to_string())
    return df

##INPUT FULL PATH FOR YOUR LAPTOP

df1 = create_df(r'C:\Users\marys\OneDrive\Documents\GitHub\SC2006-Software-Engineering_Team_RuntimeError\appname\app\dataset\secondhand.kml', "Second-hand goods")
df2 = create_df(r'C:\Users\marys\OneDrive\Documents\GitHub\SC2006-Software-Engineering_Team_RuntimeError\appname\app\dataset\cash-for-trash-kml.kml', "Cash for trash")


#initialise df4 for lighting waste
path =r'C:\Users\marys\OneDrive\Documents\GitHub\SC2006-Software-Engineering_Team_RuntimeError\appname\app\dataset\lighting-waste-collection-points-kml.kml'

d = {'ADDRESSPOSTALCODE': [],  # attributes, landx,landy,photourl
     'DESCRIPTION': [],
     'ADDRESSBUILDINGNAME': [],
     'ADDRESSUNITNUMBER': [],
     'ADDRESSBLOCKHOUSENUMBER': [],
     'HYPERLINK': [],
     'ADDRESSFLOORNUMBER': [],
     'NAME': [],  # inc_crc, fmel_upd_d
     'ADDRESSSTREETNAME': []}
keys = list(d.keys())

with open(path) as data:
    kml_soup = BeautifulSoup(data, 'lxml-xml')  # Parse as XML

descriptions = kml_soup.find_all('description')
for description in descriptions:
    html_soup = BeautifulSoup(description.text, 'lxml')  # Parse as HTML
    tables = html_soup.find_all('table')
    # print(len(tables))
    for table in tables:
        rows = table.find_all('tr')
        count = 0
        # print("rows", rows)
        for row in rows:
            # print("curr row",row)
            # row_names = table.find_all('th')
            # print("row_name", row_names)
            if count == 0 or count == 1 or count == 2 or count == 7 or count==12 or count == 14 or count == 15:
                count += 1
                continue
            cols = row.find_all('td')
            cols = str(cols).replace('[<td>', '')
            cols = cols.replace('</td>]', '')
            # if cols == '':
            #     print("none")
            # print("count ", count)
            # print(cols)
            if count== 13:
                d[keys[count - 5]].append(cols)
            elif count >=8:
                d[keys[count - 4]].append(cols)
            else:
                d[keys[count - 3]].append(cols)

            count += 1
            # print("cols", cols)
            # print(d)
            # for v in d.values():
            #     print(len(v))

df4 = pd.DataFrame(d)
# print(df.to_string())
coord_count = 0
latitude = []
longitude = []
for coords in kml_soup.find_all('coordinates'):

    # Take coordinate string from KML and break it up into [Lat,Lon,Lat,Lon...] to get CSV row
    space_splits = coords.string.split(" ")
    # print(space_splits)

    for split in space_splits:
        # Note: because of the space between <coordinates>" "-80.123, we slice [1:]
        comma_split = split.split(',')
        # lattitude
        latitude.append(comma_split[1])
        # df.iloc[coord_count]["latitude"] = comma_split[1]

        # longitude
        longitude.append(comma_split[0])
        # df.iloc[coord_count]["longitude"] = comma_split[0]
        coord_count += 1

# print(len(latitude))
# print(len(longitude))
df4['LATITUDE'] = latitude
df4['LONGITUDE'] = longitude
df4['CATEGORY'] = "Lighting Waste"

#initialise df3 for e-waste

path =r'C:\Users\marys\OneDrive\Documents\GitHub\SC2006-Software-Engineering_Team_RuntimeError\appname\app\dataset\e-waste-recycling-kml.kml'


d2 = {'NAME': [],
     'ADDRESSPOSTALCODE': [],  # attributes, landx,landy,photourl
     'HYPERLINK': [],
     'ADDRESSUNITNUMBER': [],
     'ADDRESSFLOORNUMBER': [],
     'ADDRESSBUILDINGNAME': [],
     'ADDRESSBLOCKHOUSENUMBER': [],
     'ADDRESSSTREETNAME': [],
     'DESCRIPTION': []  # inc_crc, fmel_upd_d
     }
keys = list(d2.keys())

with open(path) as data:
    kml_soup = BeautifulSoup(data, 'lxml-xml')  # Parse as XML

descriptions = kml_soup.find_all('description')
for description in descriptions:
    html_soup = BeautifulSoup(description.text, 'lxml')  # Parse as HTML
    tables = html_soup.find_all('table')
    # print(len(tables))
    for table in tables:
        rows = table.find_all('tr')
        count = 0
        # print("rows", rows)
        for row in rows:
            # print("curr row",row)
            # row_names = table.find_all('th')
            # print("row_name", row_names)
            if count == 0 or count == 2 or count == 3 or count == 5 or count==13 or count == 14:
                count += 1
                continue
            cols = row.find_all('td')
            cols = str(cols).replace('[<td>', '')
            cols = cols.replace('</td>]', '')
            # if cols == '':
            #     print("none")
            # print("count ", count)
            # print(cols)
            if count== 1:
                d2[keys[count - 1]].append(cols)
            elif count ==4:
                d2[keys[count - 3]].append(cols)
            else:
                d2[keys[count - 4]].append(cols)

            count += 1
            # print("cols", cols)
            # print(d)
            # for v in d.values():
            #     print(len(v))

df3 = pd.DataFrame(d2)
# print(df.to_string())
coord_count = 0
latitude = []
longitude = []
for coords in kml_soup.find_all('coordinates'):

    # Take coordinate string from KML and break it up into [Lat,Lon,Lat,Lon...] to get CSV row
    space_splits = coords.string.split(" ")
    # print(space_splits)

    for split in space_splits:
        # Note: because of the space between <coordinates>" "-80.123, we slice [1:]
        comma_split = split.split(',')
        # lattitude
        latitude.append(comma_split[1])
        # df.iloc[coord_count]["latitude"] = comma_split[1]

        # longitude
        longitude.append(comma_split[0])
        # df.iloc[coord_count]["longitude"] = comma_split[0]
        coord_count += 1

# print(len(latitude))
# print(len(longitude))
df3['LATITUDE'] = latitude
df3['LONGITUDE'] = longitude
df3['CATEGORY'] = "E-Waste"
# print(df3.to_string())

frames = [df1, df2, df3, df4]
combined_df = pd.concat(frames, ignore_index=True)


for i in range(0, 518):
    if combined_df.iloc[i]['CATEGORY'] == "Lighting Waste":
        print(combined_df.iloc[i])

