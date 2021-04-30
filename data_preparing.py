import pandas as pd
import unidecode
import string


def change_name(name):
    """
    string -> string

    Function that puts Player column of two
    datasets under one string pattern.
    Gets rid of non-English letters, English
    appendices such as Jr. III etc., redundant
    symbols.
    :param name: string
    :return: change name

    """
    name = name.strip()
    name = unidecode.unidecode(name)
    name = name.split()[0] + " " + name.split()[1]

    for symbol in string.punctuation:
        if symbol in name:
            name = name.replace(symbol, '')

    return name


def replace_missing(df):
    """
    df -> df

    Replace missing values of a dataframe
    with the average of a column to avoid
    outliers.
    :param df: dataframe
    :return: dataframe with replace values.

    """
    no_missing_set = df.dropna(subset=df.columns)
    avg_values = {}
    for column in no_missing_set.columns:
        if pd.api.types.is_numeric_dtype(no_missing_set[column]):
            avg_values[column] = no_missing_set[column].median()

    for column in list(df.columns):
        if column in avg_values:
            df[column] = df[column].fillna(avg_values[column])
    return df


# reading salaries dataset and preparing the data
salaries = pd.read_csv('nba_salaries.csv')
salaries.drop(columns=['Unnamed: 0', '2019/20(*)'], inplace=True)
salaries['2019/20'] = salaries['2019/20'].apply(lambda x: (x.replace(',', '').replace('$', '')))
salaries['Salary'] = pd.to_numeric(salaries['2019/20'])
salaries = salaries[['Player', 'Salary']]
salaries.sort_values(by=['Player'], inplace=True)
salaries['Player'] = salaries['Player'].apply(change_name)

# reading statistic dataset and preparing the data
statistics = pd.read_csv('nba_2020_per_game.csv')
statistics.drop(['ORB', 'DRB'], axis='columns', inplace=True)
statistics.sort_values(by=['Player'], inplace=True)
statistics.drop_duplicates(subset=['Player'], inplace=True)
statistics['Player'] = statistics['Player'].apply(change_name)
statistics = replace_missing(statistics)

# reading advanced statistics dataset and preparing the data
advanced = pd.read_csv('nba_2020_advanced.csv')
advanced['Player'] = advanced['Player'].apply(change_name)
advanced.sort_values(by=['Player'], inplace=True)
advanced.drop_duplicates(subset=['Player'], inplace=True)
advanced.drop(columns=['Pos', 'Age', 'Tm', 'G', 'MP'], inplace=True)
advanced = replace_missing(advanced)

# merging total statistics
stats = pd.merge(advanced, statistics, how='inner', on=['Player'])

# reading dataset about NBA drafts
drafts = pd.read_csv('NBA_Full_Draft_1947-2018.csv')
drafts['Player'] = drafts['Player'].apply(change_name)
drafts = drafts[['Player', 'Pick']]

# reading dataset about NBA drafts for year 2019
draft_2019 = pd.read_csv('nba_pick_2019.csv')
draft_2019['Pick'] = draft_2019['Pk']
draft_2019 = draft_2019[['Player', 'Pick']]
draft_2019['Player'] = draft_2019['Player'].apply(change_name)
drafts = pd.concat([drafts, draft_2019])

# merging final dataframes and retrieving the prepared data
pre_result = pd.merge(stats, salaries, how='inner')
result = pd.merge(pre_result, drafts, how='left', on='Player')
result['Pick'] = result['Pick'].fillna(61)
result['Pick'] = result['Pick'].apply(lambda x: int(x))
result[list(result.columns)] = result[list(result.columns)].replace(0.0, 0.001)
result.to_csv('nba/NBA_stats_salary_2019-2020.csv')
