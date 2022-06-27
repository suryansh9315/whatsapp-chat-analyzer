import streamlit as st
from PreProcessor import dataframe
from urlextract import URLExtract
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import seaborn as sns

extractor = URLExtract()
st.sidebar.title("Whatsapp Chat Analyser")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode()
    with open('WCWA.txt', 'w', encoding='UTF8') as f:
        f.write(data)
    df = dataframe()

    user_list = df['name'].unique().tolist()
    user_list.remove('Group Notification')
    user_list.sort()
    user_list.insert(0, 'Overall')

    option = st.sidebar.selectbox(
        'Show Analysis wrt ?',
        user_list)
    st.sidebar.write('You selected:', option)

    if st.sidebar.button("Show Analysis"):
        st.title('Top Statistics')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if option == 'Overall':
                st.header("Total Messages")
                st.title(df.shape[0])
            else:
                st.header("Total Messages")
                st.title(df[df['name'] == option].shape[0])

        with col2:
            if option == 'Overall':
                words = []
                for i in df['msg']:
                    for y in i.split():
                        words.append(y)
                st.header("Total Words")
                st.title(len(words))
            else:
                words = []
                for i in df[df['name'] == option]['msg']:
                    for y in i.split():
                        words.append(y)
                st.header("Total Words")
                st.title(len(words))

        with col3:
            if option == 'Overall':
                st.header('Media Shared')
                st.title(df[df['msg'] == ' <Media omitted>'].shape[0])
            else:
                st.header('Media Shared')
                st.title(df[df['name'] == option][df['msg'] == ' <Media omitted>'].shape[0])

        with col4:
            if option == 'Overall':
                links = []
                for i in df['msg']:
                    link = extractor.find_urls(i)
                    for j in link:
                        links.append(j)
                st.header('Total Linkss')
                st.title(len(links))
            else:
                links = []
                for i in df[df['name'] == option]['msg']:
                    link = extractor.find_urls(i)
                    for j in link:
                        links.append(j)
                st.header('Total Linkss')
                st.title(len(links))

        if option == 'Overall':
            temp = df[df['name'] != 'Group Notification']
            temp = temp[temp['msg'] != ' <Media omitted>']

            st.title('Monthly Timeline')
            timeline = df.groupby(['year', 'month']).count()['msg'].reset_index()
            time = []
            for i in range(timeline.shape[0]):
                time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
            timeline['time'] = time
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['msg'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.title('Daily Timeline')
            daily_timeline = df.groupby('only-date').count()['msg'].reset_index()
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only-date'], daily_timeline['msg'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.title('Activity Map')
            col1, col2 = st.columns(2)
            with col1:
                st.header("Most Busy Day")
                busy_day = df['day_name'].value_counts().reset_index().rename(
                    columns={'index': 'day', 'day_name': 'count'})
                fig, ax = plt.subplots()
                ax.bar(busy_day['day'], busy_day['count'])
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.header('Most Busy Month')
                busy_month = df['month'].value_counts().reset_index().rename(
                    columns={'index': 'month', 'month': 'count'})
                fig, ax = plt.subplots()
                ax.bar(busy_month['month'], busy_month['count'], color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title("Weekly Activity Map")
            fig, ax = plt.subplots()
            ax = sns.heatmap(
                df.pivot_table(index='day_name', columns='period', values='msg', aggfunc='count').fillna(0))
            plt.yticks(rotation='horizontal')
            st.pyplot(fig)

            st.title('Most Busy User')
            x = df['name'].value_counts().head(10)
            df2 = round((df['name'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
                columns={'index': 'name', 'name': 'percent'})
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(df2)

            st.title("Wordcloud")
            wc = WordCloud(height=500, width=500, min_font_size=10, background_color='white')
            df_wc = wc.generate(temp['msg'].str.cat(sep=" "))
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            st.title('Most Common Words')
            f = open('stop_hinglish.txt', 'r')
            stop_words = f.read()
            f.close()

            words = []
            for message in temp['msg']:
                for word in message.lower().split():
                    if word not in stop_words:
                        words.append(word)

            most_common = pd.DataFrame(Counter(words).most_common(20))
            fig, ax = plt.subplots()
            ax.barh(most_common[0], most_common[1])
            st.pyplot(fig)

            st.title('Emojis Analysis')
            emojis = []
            for message in temp['msg']:
                emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
            e_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(e_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(e_df[1].head(10), labels=e_df[0].head(10), autopct="%0.2f")
                st.pyplot(fig)

        else:
            temp2 = df[df['name'] == option]
            temp = df[df['name'] != 'Group Notification']
            temp = temp[temp['msg'] != ' <Media omitted>']
            temp = temp[temp['name'] == option]

            st.title('Monthly Timeline')
            timeline = temp2.groupby(['year', 'month']).count()['msg'].reset_index()
            time = []
            for i in range(timeline.shape[0]):
                time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
            timeline['time'] = time
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['msg'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.title('Daily Timeline')
            daily_timeline = temp2.groupby('only-date').count()['msg'].reset_index()
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only-date'], daily_timeline['msg'])
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.title('Activity Map')
            col1, col2 = st.columns(2)
            with col1:
                st.header("Most Busy Day")
                busy_day = temp2['day_name'].value_counts().reset_index().rename(
                    columns={'index': 'day', 'day_name': 'count'})
                fig, ax = plt.subplots()
                ax.bar(busy_day['day'], busy_day['count'])
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.header('Most Busy Month')
                busy_month = temp2['month'].value_counts().reset_index().rename(
                    columns={'index': 'month', 'month': 'count'})
                fig, ax = plt.subplots()
                ax.bar(busy_month['month'], busy_month['count'], color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title("Weekly Activity Map")
            fig, ax = plt.subplots()
            ax = sns.heatmap(
                temp2.pivot_table(index='day_name', columns='period', values='msg', aggfunc='count').fillna(0))
            plt.yticks(rotation='horizontal')
            st.pyplot(fig)

            st.title("Wordcloud")
            wc = WordCloud(height=500, width=500, min_font_size=10, background_color='white')
            df_wc = wc.generate(temp['msg'].str.cat(sep=" "))
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            st.title('Most Common Words')
            f = open('stop_hinglish.txt', 'r')
            stop_words = f.read()
            f.close()

            words = []
            for message in temp['msg']:
                for word in message.lower().split():
                    if word not in stop_words:
                        words.append(word)

            most_common = pd.DataFrame(Counter(words).most_common(20))
            fig, ax = plt.subplots()
            ax.barh(most_common[0], most_common[1])
            st.pyplot(fig)

            st.title('Emojis Analysis')
            emojis = []
            for message in temp['msg']:
                emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
            e_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(e_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(e_df[1].head(10), labels=e_df[0].head(10), autopct="%0.2f")
                st.pyplot(fig)
