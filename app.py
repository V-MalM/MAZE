from flask import Flask, render_template, redirect, request
import json
from flask.json import jsonify
from sqlalchemy import create_engine
import pandas as pd
import os


app = Flask(__name__)

# Creating an engine to connect to postgresql database 'MAZE'

server='ec2-54-147-126-173.compute-1.amazonaws.com'
port='5432'
db_user='ihrwvwmlryxtps'
db='d84rgddae1lb9t'
db_pass=os.environ.get('DB_PASS', '')
db_url=f'postgresql://{db_user}:{db_pass}@{server}:{port}/{db}'
# db_url=#the environment variable called POSTGRES_URL
my_engine=create_engine(db_url)

# creating connection
connection = my_engine.connect()

# fetch states 
get_states = "select distinct state_fips, sabbr, sname from  maze_data order by sabbr"
               
               
us_museum_query = "select state_fips, sabbr, museum_type_id, museum_type , "\
            " count(museum_id) as total_museums "\
            " from maze_data group by state_fips, sabbr, museum_type_id, "\
            " museum_type order by sabbr"
us_museum_df = pd.read_sql(us_museum_query, connection)


total_museums = 0
total_zoo_count	= 0
total_aqua_count = 0
total_nc_count = 0
prev_county = 0
ctr = 0
json_state_string = []

for index,row in us_museum_df.iterrows():
    if index == 0 :
        prev_state = row['state_fips']
              
    if row['state_fips'] == prev_state :
        if ctr == 0:
            curr_state_fips =  row['state_fips'] 
            curr_sabbr =  row['sabbr'] 
        
        if (row['museum_type_id'] == 1 or \
            row['museum_type_id'] == 3 or \
            row['museum_type_id'] == 4 or \
            row['museum_type_id'] == 5 or \
            row['museum_type_id'] == 7 or \
            row['museum_type_id'] == 8 or \
            row['museum_type_id'] == 9) :
            total_museums = total_museums + row['total_museums']
            prev_state =  row['state_fips'] 
        elif row['museum_type_id'] == 2 :
            total_nc_count = row['total_museums']    
        elif row['museum_type_id'] == 6 :
            total_zoo_count = row['total_museums']     
        elif row['museum_type_id'] == 10 :
            total_aqua_count = row['total_museums']               
    else:
        totals_state_dict = {'state_fips':curr_state_fips,'sabbr':curr_sabbr, 'total_museums':total_museums, \
            'total_zoo_count': total_zoo_count, 'total_aqua_count':total_aqua_count,\
            'total_nc_count':total_nc_count}
          
        json_state_string.append(totals_state_dict)

        prev_state =  row['state_fips']     
        ctr = 0  
        total_museums = 0
        total_zoo_count	= 0
        total_aqua_count = 0
        total_nc_count = 0
        if (row['museum_type_id'] == 1 or \
            row['museum_type_id'] == 3 or \
            row['museum_type_id'] == 4 or \
            row['museum_type_id'] == 5 or \
            row['museum_type_id'] == 7 or \
            row['museum_type_id'] == 8 or \
            row['museum_type_id'] == 9) :
            total_museums = row['total_museums']
        elif row['museum_type_id'] == 2 :
            total_nc_count = row['total_museums']    
        elif row['museum_type_id'] == 6 :
            total_zoo_count = row['total_museums']     
        elif row['museum_type_id'] == 10 :
            total_aqua_count = row['total_museums']
    if index+1 == len(us_museum_df) :   

        totals_state_dict = {'state_fips':row['state_fips'], 'sabbr':row['sabbr'], 'total_museums':total_museums, \
        'total_zoo_count': total_zoo_count, 'total_aqua_count':total_aqua_count,\
        'total_nc_count':total_nc_count}
   
        json_state_string.append(totals_state_dict)

    ctr = ctr + 1   
    curr_state_fips =  row['state_fips'] 
    curr_sabbr =  row['sabbr']  
us_list = json_state_string
 

# us_all_museum_query = "select museum_name, latitude, longitude, "\
#     " state_fips,county_fips from maze_data "\
# " where latitude != 0 order by county_fips"


us_all_museum_query = "select museum_name, museum_type_id, museum_type, latitude, longitude,"\
 "street_add_phyloc, city_phyloc, zip_phyloc, phone_number,"\
 "county_fips,state_fips,sabbr,sname from maze_data "\
" where latitude != 0 order by county_fips"

us_all_museum_df = pd.read_sql(us_all_museum_query, connection)

us_all_result = us_all_museum_df.to_json(orient="records")
us_mus_list = json.loads(us_all_result)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/API")
def API():
    return jsonify(us_list)

@app.route("/APIM")
def APIM():
# create a json file here 
    # file_path = os.path.join(os.getcwd(),'Maze_Dashboard\static\js','data.js')
    # print(file_path)
    # jsonString = "data =" + json.dumps(us_mus_list) 
    # jsonFile = open(file_path, "w")
    # jsonFile.write(jsonString)
    # jsonFile.close()
    

    return jsonify(us_mus_list)   

# @app.route("/APIP")
# def APIP():   


# Code 9/10/2021######################################################################
@app.route("/APITOPM/<sta>/<cot>/<cty>")
def sta(sta,cot,cty):
    if (str(sta) == "0" and str(cot) == "0" and str(cty) == "0"):
        get_top_mus_query = "select * from us_top_reviewed limit 5"
    elif (str(sta) != "0" and str(cot) == "0" and str(cty) == "0"):
        get_top_mus_query = "select * from us_top_reviewed where state_fips ="+str(sta)+"  limit 5"
        # print(get_top_mus_query)
    elif (str(sta) != "0" and str(cot) != "0" and str(cty) == "0"):
        get_top_mus_query = "select * from us_top_reviewed where fips_county ="+str(cot)+"  limit 5"
    elif (str(sta) != "0" and str(cot) != "0" and str(cty) != "0"):
        get_top_mus_query = "select * from us_top_reviewed where fips_county ="+str(cot)+" and upper(city_phyloc) ='" + str(cty) + "' limit 5"
        # print (get_top_mus_query)

    get_top_reviewed = pd.read_sql(get_top_mus_query,connection)
    top_reviewed = get_top_reviewed.to_json(orient="records")
    top_reviewed = json.loads(top_reviewed)

    return jsonify(top_reviewed)    

         
# Code 9/10/2021######################################################################     
         



@app.route("/APIREV/<st>/<ct>/<cy>")
def st(st,ct,cy):
    if (str(st) == "0" and str(ct) == "0" and str(cy) == "0"):
        get_top_reve_making_query = 'select distinct short_legal_name as "legal_name", revenue from maze_data where '\
        " revenue > 0 "\
        "order by revenue desc limit 10 "        
    elif (str(st) != "0" and str(ct) == "0" and str(cy) == "0"):
        get_top_reve_making_query = 'select distinct short_legal_name as "legal_name", revenue from maze_data where '\
        "state_fips  ="+str(st)+"  and revenue > 0 "\
        "order by revenue desc limit 10 "
    elif (str(st) != "0" and str(ct) != "0" and str(cy) == "0"):
        get_top_reve_making_query = 'select distinct short_legal_name as "legal_name", revenue from maze_data where '\
        "state_fips  ="+str(st)+" and county_fips = "+str(ct)+" and revenue > 0 "\
        "order by revenue desc limit 10 "    
    elif (str(st) != "0" and str(ct) != "0" and str(cy) != "0"):
        get_top_reve_making_query = 'select distinct short_legal_name as "legal_name", revenue from maze_data where '\
        " county_fips = "+str(ct)+" and city_phyloc ='"+str(cy)+"' "\
        " and revenue > 0 "\
        "order by revenue desc limit 10 "           
    
    get_top_reve_making = pd.read_sql(get_top_reve_making_query,connection)
    top_reve_making = get_top_reve_making.to_json(orient="records")
    top_reve_making = json.loads(top_reve_making)

    return jsonify(top_reve_making)



@app.route("/APIHM")
def APIHM():

    us_muse_type_query = "select * from maze_mus_data_all_states_grouped_by_mus_type"
    us_muse_types = pd.read_sql(us_muse_type_query, connection)
    # total_museums = 0
    prev_state = 0
    ctr = 0
    state_dict = {}
    state_coord = []
    locations = []

    for index,row in us_muse_types.iterrows():
        if index == 0 :
            prev_state = row['state_fips']
                
        if row['state_fips'] == prev_state :
            if ctr == 0:
                curr_state_fips =  row['state_fips'] 
                curr_sabbr =  row['sabbr'] 
                curr_lat = row['latitude']
                curr_lon = row['longitude']

            state_dict[row['museum_type']] = row['total_museums']    
        else:        
            # print(curr_state_fips, curr_sabbr, curr_lat, curr_lon)
            state_coord.append(curr_state_fips)
            state_coord.append(curr_sabbr)
            state_coord.append(curr_lat)
            state_coord.append(curr_lon)
            state_dict['coordinates'] = state_coord
            locations.append(state_dict)

            prev_state =  row['state_fips']     
            ctr = 0  
            # total_museums = 0
            state_coord = []
            state_dict = {}

            
        if index+1 == len(us_muse_types) :   
            # print(index+1,len(us_muse_types))    
            # print('last',row['state_fips'], row['sabbr'], row['latitude'], row['longitude'])
            state_coord.append(row['state_fips'])
            state_coord.append(row['sabbr'])
            state_coord.append(row['latitude'])
            state_coord.append(row['longitude'])
            state_dict['coordinates'] = state_coord
            locations.append(state_dict)
            

        ctr = ctr + 1   
        curr_state_fips =  row['state_fips'] 
        curr_sabbr =  row['sabbr']
        curr_lat = row['latitude']
        curr_lon = row['longitude'] 
        state_dict[row['museum_type']] = row['total_museums']  

    return jsonify(locations)  


@app.route("/API/<state>")
def state(state):
    # state = 2
    state_museum_query = "select county_fips, county, museum_type_id, museum_type , "\
        "count(museum_id) as total_museums "\
                        " from maze_data where state_fips ="+str(state)+" group by county_fips, "\
                        " county, museum_type_id, museum_type  "\
                        " order by county"
    s_museum_df = pd.read_sql(state_museum_query, connection)
    

    total_museums = 0
    total_zoo_count	= 0
    total_aqua_count = 0
    total_nc_count = 0
    prev_county = 0
    ctr = 0
    json_county_string = []

    for index,row in s_museum_df.iterrows():
        if index == 0 :
            prev_county = row['county_fips']
                
        if row['county_fips'] == prev_county :
            if ctr == 0:
                curr_county =  row['county'] 
            
            if (row['museum_type_id'] == 1 or \
                row['museum_type_id'] == 3 or \
                row['museum_type_id'] == 4 or \
                row['museum_type_id'] == 5 or \
                row['museum_type_id'] == 7 or \
                row['museum_type_id'] == 8 or \
                row['museum_type_id'] == 9) :
                total_museums = total_museums + row['total_museums']
                prev_county =  row['county_fips'] 
            elif row['museum_type_id'] == 2 :
                total_nc_count = row['total_museums']    
            elif row['museum_type_id'] == 6 :
                total_zoo_count = row['total_museums']     
            elif row['museum_type_id'] == 10 :
                total_aqua_count = row['total_museums']               
        else:
            totals_dict = {'county_x':curr_county, 'total_museums':total_museums, \
                'total_zoo_count': total_zoo_count, 'total_aqua_count':total_aqua_count,\
                'total_nc_count':total_nc_count}
            # print (totals_dict)    
            json_county_string.append(totals_dict)

            # print (curr_county, total_museums, total_zoo_count, total_aqua_count,total_nc_count )
            prev_county =  row['county_fips']     
            ctr = 0  
            total_museums = 0
            total_zoo_count	= 0
            total_aqua_count = 0
            total_nc_count = 0
            if (row['museum_type_id'] == 1 or \
                row['museum_type_id'] == 3 or \
                row['museum_type_id'] == 4 or \
                row['museum_type_id'] == 5 or \
                row['museum_type_id'] == 7 or \
                row['museum_type_id'] == 8 or \
                row['museum_type_id'] == 9) :
                total_museums = row['total_museums']
            elif row['museum_type_id'] == 2 :
                total_nc_count = row['total_museums']    
            elif row['museum_type_id'] == 6 :
                total_zoo_count = row['total_museums']     
            elif row['museum_type_id'] == 10 :
                total_aqua_count = row['total_museums']
        if index+1 == len(s_museum_df) :   

            # print (row['county'] , total_museums, total_zoo_count, total_aqua_count,total_nc_count )

            totals_dict = {'county_x':row['county'], 'total_museums':total_museums, \
            'total_zoo_count': total_zoo_count, 'total_aqua_count':total_aqua_count,\
            'total_nc_count':total_nc_count}
            # print (totals_dict)    
            json_county_string.append(totals_dict)

        ctr = ctr + 1   
        curr_county = row['county']   
    return jsonify(json_county_string)


@app.route("/API/<state>/<county>")
def county(state,county):
    # county = 41017
    county_museum_query = "select city_phyloc, museum_type_id, museum_type , count(museum_id) as total_museums "\
                            " from maze_data where county_fips ="+str(county)+" group by city_phyloc, "\
                            "museum_type_id, museum_type order by city_phyloc"
    ct_museum_df = pd.read_sql(county_museum_query, connection)

    total_museums = 0
    total_zoo_count	= 0
    total_aqua_count = 0
    total_nc_count = 0
    prev_city = 0
    ctr = 0
    json_city_string = []

    for index,row in ct_museum_df.iterrows():
        if index == 0 :
            prev_city = row['city_phyloc']
                
        if row['city_phyloc'] == prev_city :
            if ctr == 0:
                curr_city =  row['city_phyloc'] 
            
            if (row['museum_type_id'] == 1 or \
                row['museum_type_id'] == 3 or \
                row['museum_type_id'] == 4 or \
                row['museum_type_id'] == 5 or \
                row['museum_type_id'] == 7 or \
                row['museum_type_id'] == 8 or \
                row['museum_type_id'] == 9) :
                total_museums = total_museums + row['total_museums']
                prev_city =  row['city_phyloc'] 
            elif row['museum_type_id'] == 2 :
                total_nc_count = row['total_museums']    
            elif row['museum_type_id'] == 6 :
                total_zoo_count = row['total_museums']     
            elif row['museum_type_id'] == 10 :
                total_aqua_count = row['total_museums']               
        else:
            city_totals_dict = {'city_phyloc':curr_city, 'total_museums':total_museums, \
                'total_zoo_count': total_zoo_count, 'total_aqua_count':total_aqua_count,\
                'total_nc_count':total_nc_count}
            # print (totals_dict)    
            json_city_string.append(city_totals_dict)

            # print (curr_county, total_museums, total_zoo_count, total_aqua_count,total_nc_count )
            prev_city =  row['city_phyloc']     
            ctr = 0  
            total_museums = 0
            total_zoo_count	= 0
            total_aqua_count = 0
            total_nc_count = 0
            if (row['museum_type_id'] == 1 or \
                row['museum_type_id'] == 3 or \
                row['museum_type_id'] == 4 or \
                row['museum_type_id'] == 5 or \
                row['museum_type_id'] == 7 or \
                row['museum_type_id'] == 8 or \
                row['museum_type_id'] == 9) :
                total_museums = row['total_museums']
            elif row['museum_type_id'] == 2 :
                total_nc_count = row['total_museums']    
            elif row['museum_type_id'] == 6 :
                total_zoo_count = row['total_museums']     
            elif row['museum_type_id'] == 10 :
                total_aqua_count = row['total_museums']
        if index+1 == len(ct_museum_df) :   

            # print (row['county'] , total_museums, total_zoo_count, total_aqua_count,total_nc_count )

            city_totals_dict = {'city_phyloc':row['city_phyloc'], 'total_museums':total_museums, \
            'total_zoo_count': total_zoo_count, 'total_aqua_count':total_aqua_count,\
            'total_nc_count':total_nc_count}
            # print (totals_dict)    
            json_city_string.append(city_totals_dict)

        ctr = ctr + 1   
        curr_city = row['city_phyloc']   
    return jsonify(json_city_string)


# #############################################################################################
@app.route("/API/<state>/<county>/<city>")
def city(state,county,city):
    state = state
    # county=20001
    city_museum_query = "select  museum_type, count(museum_id) as total_museums from maze_data "\
                        "where county_fips = "+str(county)+ " and "\
                            "city_phyloc ='"+str(city)+"' group by museum_type "\
                        " order by museum_type"
    city_museum_df = pd.read_sql(city_museum_query, connection)

    cit_result = city_museum_df.to_json(orient="records")
    city_list = json.loads(cit_result)
    return jsonify(city_list)
###############################################################################################    
    
@app.route("/dashboard",methods=["GET", "POST"])
def dashboard():

    selected_state =  ""
    selected_county = ""
    selected_city = ""
    county_list = ""
    city_list = ""



    if request.method == "POST":
        selected_state = request.form["SelState"]
        selected_county = request.form["SelCounty"]
        selected_city = request.form["SelCity"]
        # selected_mtype = request.form.getlist('mtype')
        # print(selected_mtype)

        if selected_state != "":
            get_counties = "select distinct sname, county_fips, county from maze_data where latitude > 0  and state_fips="+selected_state+' order by county '

            county_list = connection.execute(get_counties)
            
            get_top_reve_data_query = 'select distinct museum_name,short_legal_name as "legal_name", revenue from maze_data where '\
            "state_fips  ="+selected_state+"  and revenue > 0 and museum_type_id not in (2,6,10) "\
            "order by revenue desc limit 1000 "
            get_top_reve_data_s = pd.read_sql(get_top_reve_data_query,connection)
            get_top_reve_data_s_df = get_top_reve_data_s[['museum_name', 'legal_name']]
            top_reve_data_s = get_top_reve_data_s_df.to_html(index=False)
            
            
            

        if selected_county != "":
            get_cities = "select distinct county,  city_phyloc from maze_data where latitude > 0 and county_fips="+selected_county+' order by city_phyloc '
            #print(get_cities)
            city_list = connection.execute(get_cities)

            get_top_reve_data_query = 'select distinct museum_name, short_legal_name as "legal_name", revenue from maze_data where '\
            "state_fips  ="+selected_state+" and county_fips = "+selected_county+" and revenue > 0 and museum_type_id not in (2,6,10) "\
            "order by revenue desc limit 100 "  
            get_top_reve_data_c = pd.read_sql(get_top_reve_data_query,connection)
            get_top_reve_data_c_df = get_top_reve_data_c[['museum_name', 'legal_name']]
            top_reve_data_c = get_top_reve_data_c_df.to_html(index=False)

        if selected_city != "":
            get_top_reve_data_query = 'select distinct museum_name, short_legal_name as "legal_name", revenue from maze_data where '\
            " county_fips = "+selected_county+" and city_phyloc ='"+selected_city+"' "\
            " and revenue > 0 and museum_type_id not in (2,6,10) "\
            "order by revenue desc limit 100 "        
            get_top_reve_data_t = pd.read_sql(get_top_reve_data_query,connection)
            get_top_reve_data_t_df = get_top_reve_data_t[['museum_name', 'legal_name']]
            top_reve_data_t = get_top_reve_data_t_df.to_html(index=False)
              
               

    
    # the results are rendered and displayed in HTML 
    mus_types = connection.execute("select * from us_museum_types order by museum_type")

    get_states = "select distinct state_fips, sabbr, sname from  maze_data where latitude > 0 order by sabbr"
    state_list = connection.execute(get_states)

    get_top_reve_data_query = 'select distinct museum_name, legal_name, revenue from maze_data where '\
            " revenue > 0 and museum_type_id not in (2,6,10) "\
            "order by revenue desc limit 100 "        
    get_top_reve_data = pd.read_sql(get_top_reve_data_query,connection)
    get_top_reve_data_df = get_top_reve_data[['museum_name', 'legal_name']]
    top_reve_data = get_top_reve_data_df.to_html(index=False)
    
    top_reve_data_temp = ""
    if selected_state == "" :
        top_reve_data_temp = top_reve_data
    elif selected_state != "" and selected_county == "" and selected_city == "":    
        top_reve_data_temp = top_reve_data_s
    elif selected_state != "" and selected_county != "" and selected_city == "": 
        top_reve_data_temp =  top_reve_data_c    
    elif selected_state != "" and selected_county != "" and selected_city != "":    
        top_reve_data_temp =  top_reve_data_t


    top_reve_data = top_reve_data.replace('\n','')
    top_reve_data = top_reve_data.replace('class="dataframe"','class="table tablipede-str"')
    top_reve_data = top_reve_data.replace('<thead>    <tr style="text-align: right;">      <th>0</th>      <th>1</th>    </tr>  </thead>','')
        
       
    return render_template("dashboard.html",  mus_types=mus_types,state_list=state_list,
    sel_state=selected_state, county_list=county_list, sel_county=selected_county, 
    city_list=city_list, sel_city=selected_city, top_reve_data_temp=top_reve_data_temp)


@app.route("/maps")
def maps():
    return render_template("maps.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000,use_reloader=False)