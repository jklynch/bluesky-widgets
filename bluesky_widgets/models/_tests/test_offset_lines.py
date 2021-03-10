from bluesky_live.run_builder import build_simple_run
import pytest

from ..plot_builders import OffsetLines
from ..plot_specs import Axes, Figure


# Make some runs to use.
runs = [
    build_simple_run(
        {"motor": [1, 2], "det": [10, 20], "det2": [15, 25]},
        metadata={"scan_id": 1 + i},
    )
    for i in range(10)
]
MAX_RUNS = 3


def test_pinned(FigureView):
    "Test Lines with 'pinned' and un-pinned runs."
    ys = ["det", "det2"]
    num_ys = len(ys)
    model = OffsetLines("motor", ys, max_runs=MAX_RUNS)
    view = FigureView(model.figure)

    # Add MAX_RUNS and then some more and check that they do get bumped off.
    for run in runs[:5]:
        model.add_run(run)
        assert len(model.runs) <= MAX_RUNS
    # why 2:5?
    assert runs[2:5] == list(model.runs)
    # TODO: test offset lines somehow

    view.close()


def test_properties(FigureView):
    "Touch various accessors"
    model = OffsetLines("c * motor", ["det"], namespace={"c": 3}, max_runs=MAX_RUNS)
    view = FigureView(model.figure)
    model.add_run(runs[0])
    assert model.runs[0] is runs[0]
    assert model.max_runs == MAX_RUNS
    assert model.x == "c * motor"
    assert model.ys == ("det",)
    assert dict(model.namespace) == {"c": 3}
    assert model.needs_streams == ("primary",)
    assert model.pinned == frozenset()

    view.close()


def test_decrease_max_runs(FigureView):
    "Decreasing max_runs should remove the runs and their associated lines."
    INITIAL_MAX_RUNS = 5
    model = OffsetLines("motor", ["det"], namespace={"c": 3}, max_runs=INITIAL_MAX_RUNS)
    view = FigureView(model.figure)
    for run in runs[:5]:
        model.add_run(run)
    assert len(model.runs) == INITIAL_MAX_RUNS
    assert len(model.figure.axes[0].artists) == INITIAL_MAX_RUNS
    # Decrease max_runs.
    model.max_runs = MAX_RUNS
    assert len(model.runs) == MAX_RUNS
    assert len(model.figure.axes[0].artists) == MAX_RUNS

    view.close()


@pytest.mark.parametrize("expr", ["det / det2", "-log(det)", "np.sqrt(det)"])
def test_expressions(expr, FigureView):
    "Test Lines with 'pinned' and un-pinned runs."
    ys = [expr]
    model = OffsetLines("motor", ys, max_runs=MAX_RUNS)
    view = FigureView(model.figure)
    model.add_run(runs[0])
    assert len(model.figure.axes[0].artists) == 1

    view.close()


@pytest.mark.parametrize(
    "func",
    [
        lambda det, det2: det / det2,
        lambda det, log: -log(det),
        lambda det, np: np.sqrt(det),
    ],
    ids=["division", "top-level-log", "np-dot-log"],
)
def test_functions(func, FigureView):
    "Test Lines with 'pinned' and un-pinned runs."
    ys = [func]
    model = OffsetLines("motor", ys, max_runs=MAX_RUNS)
    view = FigureView(model.figure)
    model.add_run(runs[0])
    assert len(model.figure.axes[0].artists) == 1

    view.close()


def test_figure_set_after_instantiation(FigureView):
    axes = Axes()
    model = OffsetLines("motor", [], axes=axes)
    assert model.figure is None
    figure = Figure((axes,), title="")
    assert model.figure is figure
    view = FigureView(model.figure)
    view.close()
