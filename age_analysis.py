#!/usr/bin/env python3

from pathlib import Path
import argparse

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from tqdm import tqdm
import statsmodels.api as sm
from scipy.stats import f_oneway


def main(args):
    df = pd.read_csv(args.in_file)
    df = df[(df.bp_tlv < 10) & (df.weight > 1) & (df.bp_tcount > 100)]
    df["wap_avg"] = df[["bp_wap_3", "bp_wap_4", "bp_wap_5"]].mean(axis=1)
    df["wt_avg"] = df[["bp_wt_3", "bp_wt_4", "bp_wt_5"]].mean(axis=1)
    df["la_avg"] = df[["bp_la_3", "bp_la_4", "bp_la_5"]].mean(axis=1)
    print(df["gender"].value_counts())
    # df = df.sample(n=282)
    df[["gender", "age", "height", "weight", "bp_tlv"]].describe().to_csv(f"{args.out_path}/demographics.csv")

    bins = [0, 55, 65, 75, 100]
    labels = ["45-55", "56-65", "66-75", "76-100"]
    df["age_category"] = pd.cut(df["age"], bins=bins, labels=labels)
    one_hot = pd.get_dummies(df.gender)
    df = df.join(one_hot)

    df_male = df[df.gender == 'Male']
    df_female = df[df.gender == 'Female']

    bparameters = ["bp_pi10", "wt_avg", "la_avg", "wap_avg",
                   "bp_tcount", "bp_airvol"]
    
    sns.regplot(x=df["height"], y=df["bp_tlv"])
    plt.savefig(f"{args.out_path}/scatterplots/height_tlv.jpg")
    plt.close()

    sns.regplot(x=df["weight"], y=df["age"])
    plt.savefig(f"{args.out_path}/scatterplots/weight_age.jpg")
    plt.close()

    list_anovas = {}

    for param in tqdm(bparameters):
        # Distribution plots for gender
        sns.displot(df, x=param, hue="gender", kind="kde")
        plt.savefig(f"{args.out_path}/distplots/gender_{param}.jpg")
        plt.close()

        # Distribution plots for age
        sns.displot(df, x=param, hue="age_category", kind="kde")
        plt.savefig(f"{args.out_path}/distplots/age_{param}.jpg")
        plt.close()

        # Age comparison graphs
        fig = sns.boxplot(data=df, x="age_category", y=param, hue="gender")
        plt.savefig(f"{args.out_path}/boxplots/age_{param}.jpg")
        plt.close()

        # Gender comparison graphs
        fig = sns.boxplot(data=df, x="gender", y=param)
        plt.savefig(f"{args.out_path}/boxplots/gender_{param}.jpg")
        plt.close()

        # Multivariate Regression Analysis using Ordinary Least Squares
        X = df[["Male", "age", "weight", "bp_tlv"]]
        X = sm.add_constant(X)
        y = df[param]
        model = sm.OLS(y, X).fit()
        with open(f"{args.out_path}/mlr/text/{param}.txt", "w") as fh:
            fh.write(model.summary().as_text())
        with open(f"{args.out_path}/mlr/csv/{param}.csv", "w") as fh:
            fh.write(model.summary().as_csv())

        # Simple Linear Regression
        for x in ["Male", "Female", "age", "weight", "bp_tlv"]:
            model = sm.OLS(y, df[x]).fit()
            with open(f"{args.out_path}/lr/text/{x}_{param}.txt", "w") as fh:
                fh.write(model.summary().as_text())
            with open(f"{args.out_path}/lr/csv/{x}_{param}.csv", "w") as fh:
                fh.write(model.summary().as_csv())
            sns.regplot(x=df[x], y=y)
            plt.savefig(f"{args.out_path}/scatterplots/{x}_{param}.jpg")
            plt.close()

        # ANOVA for age
        male_anova = f_oneway(*[s for idx, s in df_male.groupby("age_category")[param]])
        female_anova = f_oneway(*[s for idx, s in df_female.groupby("age_category")[param]])

        list_anovas[f"male_{param}"] = male_anova
        list_anovas[f"female_{param}"] = female_anova

    df_anova = pd.DataFrame.from_dict(list_anovas)
    df_anova.to_csv(f"{args.out_path}/anova.csv")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file", type=str, help="Input summary file.")
    parser.add_argument("out_path", type=str, help="Output directory path.")
    args = parser.parse_args()
    main(args)
