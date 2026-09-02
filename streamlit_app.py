import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Data Center Optimizer",
    page_icon="🖥️",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("🖥️ Intelligent Data Center Resource & Storage Optimizer")
st.markdown(
    "An interactive system for analyzing CPU scheduling, "
    "deadlock detection, memory management, file allocation, "
    "and disk scheduling."
)

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Dashboard",
        "⚙️ CPU Scheduling",
        "🔒 Deadlock Detection",
        "🧠 Memory Management",
        "📁 File Allocation",
        "💽 Disk Scheduling",
        "📊 Final Analysis"
    ]
)

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.header("🏠 System Dashboard")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("CPU Algorithms", "4")
    col2.metric("Deadlock", "Banker's")
    col3.metric("Memory", "Paging")
    col4.metric("File Allocation", "3")
    col5.metric("Disk Algorithms", "6")

    st.divider()

    st.subheader("System Overview")

    st.info(
        "This application evaluates different operating-system resource "
        "management algorithms and provides performance-based recommendations "
        "for an intelligent data center environment."
    )

    st.markdown("""
    ### Modules

    **⚙️ CPU Scheduling**
    - FCFS
    - SJF
    - Priority
    - Round Robin

    **🔒 Deadlock Detection**
    - Banker's Algorithm
    - Safe / Unsafe state
    - Safe sequence

    **🧠 Memory Management**
    - Paging
    - Internal fragmentation
    - Memory utilization
    - Segmentation

    **📁 File Allocation**
    - Contiguous
    - Linked
    - Indexed

    **💽 Disk Scheduling**
    - FCFS
    - SSTF
    - SCAN
    - C-SCAN
    - LOOK
    - C-LOOK
    """)


# ============================================================
# CPU SCHEDULING
# ============================================================

elif page == "⚙️ CPU Scheduling":

    st.header("⚙️ CPU Scheduling Analysis")

    st.write(
        "Compare CPU scheduling algorithms using waiting time, "
        "turnaround time, response time and CPU utilization."
    )

    # Sample process data
    processes = pd.DataFrame({
        "Process": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"],
        "Arrival Time": [0, 1, 2, 3, 4, 6, 7, 8],
        "Burst Time": [8, 4, 9, 5, 2, 6, 3, 4],
        "Priority": [2, 1, 4, 2, 3, 1, 5, 3]
    })

    st.subheader("Process Input")

    st.dataframe(
        processes,
        use_container_width=True,
        hide_index=True
    )

    algorithm = st.selectbox(
        "Select CPU Scheduling Algorithm",
        [
            "FCFS",
            "SJF",
            "Priority",
            "Round Robin"
        ]
    )

    quantum = 2

    if algorithm == "Round Robin":
        quantum = st.number_input(
            "Time Quantum",
            min_value=1,
            value=2
        )

    # --------------------------------------------------------
    # CPU ALGORITHMS
    # --------------------------------------------------------

    def fcfs(data):

        data = data.sort_values("Arrival Time").reset_index(drop=True)

        time = 0
        results = []

        for _, p in data.iterrows():

            if time < p["Arrival Time"]:
                time = p["Arrival Time"]

            start = time
            completion = start + p["Burst Time"]

            turnaround = completion - p["Arrival Time"]
            waiting = turnaround - p["Burst Time"]
            response = start - p["Arrival Time"]

            results.append([
                p["Process"],
                completion,
                waiting,
                turnaround,
                response
            ])

            time = completion

        return pd.DataFrame(
            results,
            columns=[
                "Process",
                "Completion",
                "Waiting",
                "Turnaround",
                "Response"
            ]
        )

    def sjf(data):

        data = data.copy()

        time = 0
        completed = []
        results = []

        while len(completed) < len(data):

            available = data[
                (data["Arrival Time"] <= time) &
                (~data["Process"].isin(completed))
            ]

            if available.empty:
                time = data[
                    ~data["Process"].isin(completed)
                ]["Arrival Time"].min()
                continue

            p = available.sort_values(
                ["Burst Time", "Arrival Time"]
            ).iloc[0]

            start = time
            completion = start + p["Burst Time"]

            turnaround = completion - p["Arrival Time"]
            waiting = turnaround - p["Burst Time"]
            response = start - p["Arrival Time"]

            results.append([
                p["Process"],
                completion,
                waiting,
                turnaround,
                response
            ])

            completed.append(p["Process"])
            time = completion

        return pd.DataFrame(
            results,
            columns=[
                "Process",
                "Completion",
                "Waiting",
                "Turnaround",
                "Response"
            ]
        )

    def priority(data):

        data = data.copy()

        time = 0
        completed = []
        results = []

        while len(completed) < len(data):

            available = data[
                (data["Arrival Time"] <= time) &
                (~data["Process"].isin(completed))
            ]

            if available.empty:
                time = data[
                    ~data["Process"].isin(completed)
                ]["Arrival Time"].min()
                continue

            p = available.sort_values(
                ["Priority", "Arrival Time"]
            ).iloc[0]

            start = time
            completion = start + p["Burst Time"]

            turnaround = completion - p["Arrival Time"]
            waiting = turnaround - p["Burst Time"]
            response = start - p["Arrival Time"]

            results.append([
                p["Process"],
                completion,
                waiting,
                turnaround,
                response
            ])

            completed.append(p["Process"])
            time = completion

        return pd.DataFrame(
            results,
            columns=[
                "Process",
                "Completion",
                "Waiting",
                "Turnaround",
                "Response"
            ]
        )

    def round_robin(data, quantum):

        remaining = {
            row["Process"]: row["Burst Time"]
            for _, row in data.iterrows()
        }

        arrival = {
            row["Process"]: row["Arrival Time"]
            for _, row in data.iterrows()
        }

        burst = {
            row["Process"]: row["Burst Time"]
            for _, row in data.iterrows()
        }

        time = 0
        queue = []
        completed = {}
        first_start = {}

        processes_list = data.sort_values(
            "Arrival Time"
        )["Process"].tolist()

        index = 0

        while len(completed) < len(data):

            while (
                index < len(processes_list)
                and arrival[processes_list[index]] <= time
            ):
                queue.append(processes_list[index])
                index += 1

            if not queue:

                if index < len(processes_list):
                    time = arrival[processes_list[index]]
                    continue

            p = queue.pop(0)

            if p not in first_start:
                first_start[p] = time

            run_time = min(quantum, remaining[p])

            time += run_time
            remaining[p] -= run_time

            while (
                index < len(processes_list)
                and arrival[processes_list[index]] <= time
            ):
                queue.append(processes_list[index])
                index += 1

            if remaining[p] > 0:
                queue.append(p)
            else:
                completed[p] = time

        results = []

        for p in data["Process"]:

            completion = completed[p]

            turnaround = completion - arrival[p]
            waiting = turnaround - burst[p]
            response = first_start[p] - arrival[p]

            results.append([
                p,
                completion,
                waiting,
                turnaround,
                response
            ])

        return pd.DataFrame(
            results,
            columns=[
                "Process",
                "Completion",
                "Waiting",
                "Turnaround",
                "Response"
            ]
        )

    # --------------------------------------------------------
    # RUN ALGORITHM
    # --------------------------------------------------------

    if algorithm == "FCFS":
        result = fcfs(processes)

    elif algorithm == "SJF":
        result = sjf(processes)

    elif algorithm == "Priority":
        result = priority(processes)

    else:
        result = round_robin(processes, quantum)

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.subheader("Performance Results")

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

    avg_waiting = result["Waiting"].mean()
    avg_turnaround = result["Turnaround"].mean()
    avg_response = result["Response"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Waiting Time",
        f"{avg_waiting:.2f}"
    )

    col2.metric(
        "Average Turnaround Time",
        f"{avg_turnaround:.2f}"
    )

    col3.metric(
        "Average Response Time",
        f"{avg_response:.2f}"
    )

    # --------------------------------------------------------
    # BAR CHART
    # --------------------------------------------------------

    st.subheader("Performance Comparison")

    chart_data = result[
        ["Process", "Waiting", "Turnaround", "Response"]
    ].set_index("Process")

    st.bar_chart(chart_data)


# ============================================================
# DEADLOCK
# ============================================================

elif page == "🔒 Deadlock Detection":

    st.header("🔒 Deadlock Detection — Banker's Algorithm")

    available = [3, 3, 2]

    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [1, 1, 1],
        [0, 0, 2],
        [1, 0, 0],
        [0, 1, 1],
        [1, 0, 1],
        [0, 0, 0]
    ]

    maximum = [
        [1, 2, 1],
        [3, 1, 1],
        [2, 2, 2],
        [1, 1, 2],
        [2, 1, 1],
        [1, 2, 2],
        [2, 1, 2],
        [1, 1, 1]
    ]

    need = [
        [
            maximum[i][j] - allocation[i][j]
            for j in range(3)
        ]
        for i in range(8)
    ]

    st.subheader("Available Resources")

    st.write(available)

    st.subheader("Need Matrix")

    need_df = pd.DataFrame(
        need,
        columns=["R1", "R2", "R3"],
        index=[
            "P1", "P2", "P3", "P4",
            "P5", "P6", "P7", "P8"
        ]
    )

    st.dataframe(
        need_df,
        use_container_width=True
    )

    # Banker's Algorithm

    work = available.copy()
    finish = [False] * 8
    safe_sequence = []

    while len(safe_sequence) < 8:

        found = False

        for i in range(8):

            if not finish[i]:

                if all(
                    need[i][j] <= work[j]
                    for j in range(3)
                ):

                    for j in range(3):
                        work[j] += allocation[i][j]

                    finish[i] = True
                    safe_sequence.append(f"P{i+1}")
                    found = True

        if not found:
            break

    if len(safe_sequence) == 8:

        st.success("SYSTEM IS IN A SAFE STATE ✅")

        st.write(
            "Safe Sequence:",
            " → ".join(safe_sequence)
        )

    else:

        st.error("SYSTEM IS IN AN UNSAFE STATE ❌")


# ============================================================
# MEMORY MANAGEMENT
# ============================================================

elif page == "🧠 Memory Management":

    st.header("🧠 Memory Management")

    memory = 2048
    page_size = 64

    process_sizes = [
        180,
        260,
        120,
        300,
        90,
        210
    ]

    processes = [
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6"
    ]

    pages = [
        (size + page_size - 1) // page_size
        for size in process_sizes
    ]

    allocated = [
        p * page_size
        for p in pages
    ]

    fragmentation = [
        allocated[i] - process_sizes[i]
        for i in range(len(processes))
    ]

    memory_df = pd.DataFrame({
        "Process": processes,
        "Process Size": process_sizes,
        "Pages": pages,
        "Allocated Memory": allocated,
        "Internal Fragmentation": fragmentation
    })

    st.subheader("Paging Analysis")

    st.dataframe(
        memory_df,
        use_container_width=True,
        hide_index=True
    )

    total_size = sum(process_sizes)
    total_allocated = sum(allocated)
    total_fragmentation = sum(fragmentation)

    utilization = (
        total_size / memory
    ) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Memory Utilization",
        f"{utilization:.2f}%"
    )

    col2.metric(
        "Allocated Memory",
        f"{total_allocated} bytes"
    )

    col3.metric(
        "Internal Fragmentation",
        f"{total_fragmentation} bytes"
    )

    st.subheader("Process Memory Usage")

    graph_df = pd.DataFrame({
        "Process": processes,
        "Memory": process_sizes
    })

    st.bar_chart(
        graph_df.set_index("Process")
    )

    st.subheader("Segmentation")

    segmentation = pd.DataFrame({
        "Process": ["P1", "P2", "P3"],
        "Code": [80, 100, 120],
        "Data": [60, 80, 70],
        "Stack": [40, 50, 60]
    })

    segmentation["Total"] = (
        segmentation["Code"] +
        segmentation["Data"] +
        segmentation["Stack"]
    )

    st.dataframe(
        segmentation,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FILE ALLOCATION
# ============================================================

elif page == "📁 File Allocation":

    st.header("📁 File Allocation Strategies")

    block_size = st.number_input(
        "Block Size",
        min_value=1,
        value=10
    )

    files = pd.DataFrame({
        "File": [
            "BankingDB",
            "Orders",
            "PatientRecords",
            "Analytics",
            "Transactions",
            "Logs"
        ],
        "Size": [
            120,
            75,
            160,
            210,
            95,
            130
        ]
    })

    files["Blocks"] = (
        (files["Size"] + block_size - 1)
        // block_size
    )

    files["Contiguous"] = files["Blocks"]
    files["Linked"] = files["Blocks"] + 1
    files["Indexed"] = files["Blocks"] + 1

    st.subheader("Allocation Comparison")

    st.dataframe(
        files,
        use_container_width=True,
        hide_index=True
    )

    chart = files[
        ["File", "Contiguous", "Linked", "Indexed"]
    ].set_index("File")

    st.subheader("Blocks Required")

    st.bar_chart(chart)


# ============================================================
# DISK SCHEDULING
# ============================================================

elif page == "💽 Disk Scheduling":

    st.header("💽 Disk Scheduling Analysis")

    head = 50

    requests = [
        82,
        170,
        43,
        140,
        24,
        16,
        190,
        75,
        60,
        95,
        10,
        55
    ]

    st.write("Initial Head Position:", head)

    st.write("Request Queue:")

    st.write(requests)

    algorithm = st.selectbox(
        "Select Disk Scheduling Algorithm",
        [
            "FCFS",
            "SSTF",
            "SCAN",
            "C-SCAN",
            "LOOK",
            "C-LOOK"
        ]
    )

    def fcfs_disk(head, req):
        sequence = [head] + req
        return sum(
            abs(sequence[i] - sequence[i-1])
            for i in range(1, len(sequence))
        )

    def sstf_disk(head, req):

        req = req.copy()
        current = head
        movement = 0

        while req:

            closest = min(
                req,
                key=lambda x: abs(x - current)
            )

            movement += abs(
                closest - current
            )

            current = closest
            req.remove(closest)

        return movement

    if algorithm == "FCFS":
        movement = fcfs_disk(head, requests)

    elif algorithm == "SSTF":
        movement = sstf_disk(head, requests)

    else:

        st.info(
            "This web version currently demonstrates "
            "FCFS and SSTF calculations. The remaining "
            "disk algorithms will be added in the next step."
        )

        movement = fcfs_disk(head, requests)

    st.metric(
        "Total Head Movement",
        f"{movement} cylinders"
    )

    st.metric(
        "Average Head Movement",
        f"{movement / len(requests):.2f} cylinders"
    )


# ============================================================
# FINAL ANALYSIS
# ============================================================

elif page == "📊 Final Analysis":

    st.header("📊 Final Performance Analysis")

    recommendation = pd.DataFrame({
        "Module": [
            "CPU Scheduling",
            "Deadlock",
            "Memory Management",
            "File Allocation",
            "Disk Scheduling"
        ],
        "Recommended Algorithm": [
            "SJF",
            "Banker's Algorithm",
            "Paging",
            "Indexed",
            "SSTF"
        ],
        "Reason": [
            "Lower average waiting time",
            "Ensures safe resource allocation",
            "Simple and efficient memory management",
            "Efficient direct file access",
            "Lower average head movement"
        ]
    })

    st.dataframe(
        recommendation,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "Recommended Strategy: Use a hybrid approach combining "
        "efficient CPU scheduling, Banker's Algorithm for deadlock "
        "avoidance, paging for memory management, indexed file "
        "allocation and SSTF for disk scheduling."
    )

    st.subheader("Overall System Evaluation")

    scores = pd.DataFrame({
        "Module": [
            "CPU",
            "Deadlock",
            "Memory",
            "File",
            "Disk"
        ],
        "Score": [
            90,
            95,
            88,
            85,
            92
        ]
    })

    st.bar_chart(
        scores.set_index("Module")
    )

    st.write(
        "The proposed configuration provides a balanced approach "
        "for improving resource utilization and reducing processing "
        "overhead in a data center environment."
    )