from myself.tools.basic import init_my_qlib
from qlib.utils import init_instance_by_config, flatten_dict
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord


def trytry():
    init_my_qlib()

    # 定义市场和基准
    market = "all"
    benchmark = "ZS000300"

    # 定义数据处理配置
    data_handler_config = {
        "start_time": "2012-01-01",
        "end_time": "2019-12-31",
        "fit_start_time": "2012-01-01",
        "fit_end_time": "2014-12-31",
        "instruments": market,
    }

    # 定义任务配置
    task = {
        "model": {
            "class": "LGBModel",
            "module_path": "qlib.contrib.model.gbdt",
            "kwargs": {
                "loss": "mse",
                "colsample_bytree": 0.8879,
                "learning_rate": 0.0421,
                "subsample": 0.8789,
                "lambda_l1": 205.6999,
                "lambda_l2": 580.9768,
                "max_depth": 8,
                "num_leaves": 210,
                "num_threads": 20,
            },
        },
        "dataset": {
            "class": "DatasetH",
            "module_path": "qlib.data.dataset",
            "kwargs": {
                "handler": {
                    "class": "Alpha158",
                    "module_path": "qlib.contrib.data.handler",
                    "kwargs": data_handler_config,
                },
                "segments": {
                    "train": ("2012-01-01", "2014-12-31"),
                    "valid": ("2015-01-01", "2016-12-31"),
                    "test": ("2017-01-01", "2019-12-31"),
                },
            },
        },
    }

    # 初始化模型和数据集
    model = init_instance_by_config(task["model"])
    dataset = init_instance_by_config(task["dataset"])

    # 开始实验并训练模型
    with R.start(experiment_name="train_model"):
        R.log_params(**flatten_dict(task))
        model.fit(dataset)
        R.save_objects(trained_model=model)
        rid = R.get_recorder().id

    # 定义回测配置
    port_analysis_config = {
        "executor": {
            "class": "SimulatorExecutor",
            "module_path": "qlib.backtest.executor",
            "kwargs": {
                "time_per_step": "day",
                "generate_portfolio_metrics": True,
            },
        },
        "strategy": {
            "class": "TopkDropoutStrategy",
            "module_path": "qlib.contrib.strategy.signal_strategy",
            "kwargs": {
                "model": model,
                "dataset": dataset,
                "topk": 50,
                "n_drop": 5,
            },
        },
        "backtest": {
            "start_time": "2017-01-01",
            "end_time": "2020-08-01",
            "account": 100000000,
            "benchmark": benchmark,
            "exchange_kwargs": {
                "freq": "day",
                "limit_threshold": 0.095,
                "deal_price": "close",
                "open_cost": 0.0005,
                "close_cost": 0.0015,
                "min_cost": 5,
            },
        },
    }

    # 执行回测和分析
    with R.start(experiment_name="backtest_analysis"):
        recorder = R.get_recorder(recorder_id=rid, experiment_name="train_model")
        model = recorder.load_object("trained_model")

        # 生成预测信号
        recorder = R.get_recorder()
        ba_rid = recorder.id
        sr = SignalRecord(model, dataset, recorder)
        sr.generate()

        # 执行回测并分析结果
        par = PortAnaRecord(recorder, port_analysis_config, "day")
        par.generate()

    print("策略回测完成！")


if __name__ == '__main__':
    trytry()
