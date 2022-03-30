from pathlib import Path


DATASETS = {
    "home_data_train": {
        "data_path": Path("../data/home-data/train.csv"),
        "features": [
            "LotFrontage", "LotArea", "OverallQual", "OverallCond", "YearBuilt", "YearRemodAdd", "MasVnrArea",
            "BsmtFinSF1", "BsmtFinSF2", "BsmtUnfSF", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF",
            "GrLivArea", "BsmtFullBath", "BsmtHalfBath", "FullBath", "HalfBath", "BedroomAbvGr", "KitchenAbvGr",
            "TotRmsAbvGrd", "Fireplaces", "GarageYrBlt", "GarageCars", "GarageArea", "WoodDeckSF",
            "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch", "PoolArea", "MiscVal",
            "MoSold", "YrSold"
        ],
        "target": "SalePrice"
    },
    "bike_sharing_day": {
        "data_path": Path("../data/bike-sharing-dataset/day.csv"),
        "features": [
            "temp", "hum", "windspeed", "season", "yr", "mnth", "holiday", "weekday", "workingday",
            "weathersit", "atemp"
        ],
        "target": "cnt"
    },
    "bike_sharing_hour": {
        "data_path": Path("../data/bike-sharing-dataset/hour.csv"),
        "features": [
            "temp", "atemp", "hum", "windspeed", "season", "yr", "mnth", "hr", "holiday", "weekday",
            "workingday", "weathersit"
        ],
        "target": "cnt"
    },
}