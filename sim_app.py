import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns



################################## BRING IN DATA and calcs ##################################
# bring in data and drop columns
results_to_date = pd.read_csv('2022_actual_results.csv')
results_to_date.drop(columns='Unnamed: 0', inplace=True)
results_to_date['player1name'] = results_to_date['player1name'].str[:22]
# aggregate to an actual table (Rather than gw points)
current_table = results_to_date.groupby(by='player1name').sum()[['tablepoints', 'player1score', 'player2score']]
current_table['pts_diff'] = current_table['player1score'] - current_table['player2score']
current_table['tablepoints'] = current_table['tablepoints'].astype(int)
current_table = current_table.sort_values(by=['tablepoints', 'player1score'], ascending=False)
col_one_list = current_table.reset_index()['player1name'].tolist()

# bring in sim data and drop columns
sim_tables = pd.read_csv('2022_simmed_results.csv')
sim_tables.drop(columns='Unnamed: 0', inplace=True)
sim_tables['player1name'] = sim_tables['player1name'].str[:22]

# bring in head to head
h2h = pd.read_csv('2022_h2h.csv')
h2h.drop(columns='Unnamed: 0', inplace=True)

# bring in playoffs over time
pot = pd.read_csv('2022_simmed_playoffs.csv')

#Top 4
top4 = sim_tables[sim_tables['Season_rank']<=4].groupby(by='player1name').count()['Season_rank'].reset_index()
top4['Top 4 finishes'] = top4['Season_rank']
top4['% of playoffs'] = top4['Top 4 finishes']/1000*100
top4['% of playoffs'] = top4['% of playoffs'].round(2).astype(str) + "%"
top4.drop(['Season_rank'], axis=1, inplace=True)
top4['odds'] = top4['Top 4 finishes']/1000*100
top4['Odds of top 4'] = ((100/top4['odds']-1)).round(2).astype(str)+'/1'
top4.drop(['odds'], axis=1, inplace=True)
top4 = top4.sort_values(by='Top 4 finishes', ascending = False)

top4_list = top4.reset_index()['player1name'].tolist()
firstpos = top4_list[0]
secondpos = top4_list[1]
thirdpos = top4_list[2]
fourthpos = top4_list[3]

# luck
results_to_date['Luck Adjusted Pts'] = np.where(results_to_date['GW_rank']<7, 1, 0)
results_to_date['Luck Adjusted Pts'] = np.where(results_to_date['GW_rank']<5, 3, results_to_date['Luck Adjusted Pts'])
u = results_to_date.groupby(by=['player1name']).sum()
u = u[['Luck Adjusted Pts', 'tablepoints', 'player1score']]
u = u.sort_values(by=['Luck Adjusted Pts', 'player1score'], ascending=False)
u['tablepoints'] = u['tablepoints'].astype(int)
u['Luck Delta'] = u['tablepoints'] - u['Luck Adjusted Pts']
u['Luck Status'] = np.where(u['Luck Delta']<0, 'Unlucky', 'Lucky')
u['Luck Status'] = np.where(u['Luck Delta']==0, 'Net Even', u['Luck Status'])
#u['Luck Status'] = np.where(u[u['Luck Delta'] == u['Luck Delta'].max()], 'MOST Unlucky', u['Luck Status'])
is_max = u['Luck Delta'].max()
is_min = u['Luck Delta'].min()
u['Luck Status'] = np.where(u['Luck Delta']==is_max, 'MOST LUCKY', u['Luck Status'])
u['Luck Status'] = np.where(u['Luck Delta']==is_min, 'MOST UNLUCKY', u['Luck Status'])
u.drop('player1score', inplace=True, axis=1)


lucky_player = u.index[u['Luck Status'] == "MOST LUCKY"][0]
unlucky_player = u.index[u['Luck Status'] == "MOST UNLUCKY"][0]







################################## HEADERS and INTRO ####################################################################

linkedinlink = '[Andy Uttley - LinkedIn](https://www.linkedin.com/in/andrewuttley/)'
mediumlink = '[Andy Uttley - Medium Blog](https://andy-uttley.medium.com/)'

st.write("# 🤖🤖 JB Simulator 🤖🤖")
gw_current = results_to_date['GW'].max()
st.write("### Data scraped up to and including GW: ", gw_current)
st.write("Simulating the remaining ", 36-gw_current, " gameweeks 1,000 times to see what might happen")
st.image('jimmy.jpeg')

##################################### headline dynamic text ###########################################

st.write("#### 🥇 The most likely playoffs places are:")
top_table = top4[['player1name', '% of playoffs']][:4]
top_table['Model confidence in making playoffs'] = top_table['% of playoffs']
top_table.drop(['% of playoffs'], axis=1, inplace=True)
top_table.set_index('player1name', inplace=True)
st.dataframe(top_table)


st.write("")
st.text(".*.*.*.*.*.*.*.*.*.*.*.")
st.write("#### 🎰 I should be so lucky")
st.write("⚽ Most UNLUCKY:   ", unlucky_player)
st.write("⚽ Most LUCKY:   ", lucky_player)
st.text(".*.*.*.*.*.*.*.*.*.*.*.")

st.write("")
st.write(" ")
###################################### show current table #########################################################
st.write("""## Current Table""")
showtable = st.checkbox("Show current table" , value=False)
if showtable:
        current_table




##################################### top 4 finish ##########################################################
st.write("## Top 4 finishes out of 1000 simulations")
top4finish = st.checkbox('Show predicted top 4 finish', value=False)
if top4finish:
        top4


##################################### crosstab ##########################################################
st.write("## End Position Matrix")
st.write("See % likelihood for each player to finish in each position across 1000 seasons")

matrixselect = st.checkbox('Show matrix', value=False)
if matrixselect:
        d = pd.crosstab([sim_tables.player1name],sim_tables.Season_rank.astype(int), rownames = ["player1name"], colnames = ["finish"])
        d = d.reindex(col_one_list)
        d = d.apply(lambda x: (x/10))
        d2 = d.style.set_precision(1)
        d2


        #e = d.style.background_gradient(cmap='Reds')
        #e

##################################### show simmed table ##########################################################
st.write("""## Underlying simulations""")
st.write("""#### See data from the 1000 simulations""")



##################################### histogram ##########################################################

showdist = st.checkbox("Show simulation distributions", value = False)
if showdist:
        # chart
        # Add histogram data
        st.write("Simulation of distribution of end of season table points scored")

        hist2 = sns.displot(sim_tables.groupby(by=['player1name','Iteration']).mean()['tablepoints'].reset_index(), x="tablepoints", hue="player1name", kind="kde", fill=True)
        st.pyplot(hist2)

        # Add histogram data
        st.write("Simulation of distribution of end of season absolute team points scored")
        hist = sns.displot(sim_tables.groupby(by=['player1name','Iteration']).mean()['player1score'].reset_index(), x="player1score", hue="player1name", kind="kde", fill=True)
        st.pyplot(hist)




showfullsim = st.checkbox("Show full simulations and average finishes", value = False)
if showfullsim:
        st.write("Average Finishes:")
        option = st.selectbox('Choose average method:', ('mean', 'median'))
        if option == "mean":
                w = sim_tables.groupby(by=['player1name']).mean().reset_index()
        elif option == "median":
                w = sim_tables.groupby(by=['player1name']).median().reset_index()
        w.drop(['Iteration', 'MaxRealWeek'], axis=1, inplace=True)
        w = w.sort_values(by=['tablepoints', 'player1score'],ascending=False)
        w

        st.write("⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽ ⚽")

st.write("## Single season simulation")
showonesim = st.checkbox("Pick a single iteration and see what happened", value=False)
if showonesim:
        # aggregate to overall finishes
        st.write("Choose a single simulation and see how it ended")
        i = st.slider("Choose a simulated season to see the GW36 table:", 1,1000, 500)
        simd = sim_tables[sim_tables['Iteration'] == i]
        simd = simd[['player1name', 'tablepoints', 'player1score', 'player2score']]
        simd.sort_values(by=['tablepoints', 'player1score'])
        simd['tablepoints'] = simd['tablepoints'].astype(int)
        st.write("Season simulation ", i, "produced the following result:")
        st.write("🥇🥇🥇 It's a HUGE WELL DONE to ", simd['player1name'].iloc[0], " who won simulation ", str(i), " 🥇🥇🥇")
        simd

st.write("## Head to Head each week...")
st.write("Shows how many weeks out of ", h2h['GWs'][0], " gameweeks that left name beat right name. Note that it only counts wins, and not weeks you would have drawn.")
h2h['% win rate'] = h2h['win_count']/h2h['GWs']*100
h2h.drop(columns='GWs', inplace=True)
pnames = h2h['player1name_left'].drop_duplicates()
make_choice = st.selectbox('Select your player:', pnames)
st.dataframe(h2h[h2h['player1name_left']==make_choice].sort_values(by='win_count', ascending=False))

        
st.write("## Current GW finishing rankings")
st.write("Real results only, how many times has each player finished in each ranked spot")
show_gw_ranks = st.checkbox("Show GW ranked finished to date", value=False)
if show_gw_ranks:
        r_ct = pd.crosstab([results_to_date.player1name], results_to_date.GW_rank.astype(int), rownames=["player1name"], colnames=["GW_rank"])
        r_ct = r_ct.reindex(col_one_list)
        r_ct

st.write("## Luck adjusted table")
st.write("Showing table if being in top 4 places gave you a win, positions 5 and 6 a draw. This removes the uncontrollable variable of your opponents score")
show_lk_ranks = st.checkbox("Show luck adjusted table", value=False)
if show_lk_ranks:
        

        
        st.write("")
        st.write("In a perfect world, the table might look a bit more like this:")
        u
        
        st.text("But the JB shield is no fairy-tale world...")
        st.write("")

        t = u['Luck Delta'].sum()
        st.write("NB: there is a difference of ", t, " points between the actual table and luck adjusted table. This is explained by the luck table always assuming 14 table points awared per wk: 4 people win, 2 people draw. The real table is volatile: sometimes 5 people win, sometimes (e.g. gw7) everyone draws, sometimes something inbetween).") 



st.write("""## How it works""")
howitworks = st.checkbox('Show user guide', value=False)
if howitworks:
        st.write("Simulate the season 1000 times over based on each Manager's previous performance.")
        st.write("### Purpose")
        st.write('Purpose \n - To answer the question: "What are the most likely outcomes at the end of the season (GW36)?" \n - This tool shows the results of many simulated finishes to the Jimmy Bullard season')
        st.write("### Methodology")
        st.write("- The model scrapes actual data from gameweeks that have happened to date \n - The remaining fixtures are simulated by taking a 'Manager Predicted Score' (MPS) in each of the remaining gameweeks, and building an end of season aggregated 'GW36 finished' table \n - The 'MPS' is simulated using the manager's historic underlying gameweek performance data, e.g. the mean, spread, standard deviation etc.  \n - The 'MPS' assumes a normal distribution (bell curve) based on the metrics outlined above, and therefore a manager's simulated performance will reflect their performance to date \n- Scores being simulated like this mean that someone who consistently scores well is likely to beat someone who incosistently scores less well, but this is not guarenteed (like in real life) as the inconsistent scorer might have a 'good week' \n - The end of season results are captured and then repeated many times (1,000); this is to account for as much of the variance in results as possible, to give as accurate as possible model guess at the most likely end of season results")
        st.write(" ### Notes")
        st.write("- The 'end of season' is defined as GW36, i.e. up to but not including the two final playoff weeks; this tool is not intended to predict who will take the trophy this year, rather who will make the playoffs \n - The model will get more accurate as the season goes on; the more 'real' data it is fed (i.e. historic gameweeks) the more accurate its predictions are and the fewer gameweeks that are simulated \n - Predicted scores do not take into account anything other than the manager's previous scoring distributions and Std Deviations. I.e. the players in a managers team, the fixtures those actual players have in the Prem, how likely a manager is to change their team are not directly reflected in the model (but indirectly are by reference to their previous performance and distributions)  \n - Whilst multiple simulations account for different outcomes, a manager's % chance of N (e.g. making playoffs, or finishing top) is not a guarentee that it is mathmatically impossible, it can only imply that it would be unlikely to happen in 1000 seasons from this point.")




################################# more info links ###################################################
st.write("### Info/Contact")
st.write(mediumlink, " | ", linkedinlink)
