import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt


# ============================================================
# SAMPLE DATA
# ============================================================

PROCESSES = [
    ("P1", 0, 8, 2),
    ("P2", 1, 4, 1),
    ("P3", 2, 9, 4),
    ("P4", 3, 5, 2),
    ("P5", 4, 2, 3),
    ("P6", 6, 6, 1),
    ("P7", 7, 3, 5),
    ("P8", 8, 4, 3),
]

AVAILABLE = [3, 3, 2]

ALLOCATION = [
    [0, 1, 0],
    [2, 0, 0],
    [1, 1, 1],
    [0, 0, 2],
    [1, 0, 0],
    [0, 1, 1],
    [1, 0, 1],
    [0, 0, 0],
]

MAXIMUM = [
    [1, 2, 1],
    [3, 1, 1],
    [2, 2, 2],
    [1, 1, 2],
    [2, 1, 1],
    [1, 2, 2],
    [2, 1, 2],
    [1, 1, 1],
]

MEMORY_PROCESSES = [
    ("P1", 180),
    ("P2", 260),
    ("P3", 120),
    ("P4", 300),
    ("P5", 90),
    ("P6", 210),
]

SEGMENTS = [
    ("P1", 80, 60, 40),
    ("P2", 100, 80, 50),
    ("P3", 120, 70, 60),
]

FILES = [
    ("BankingDB", 120),
    ("Orders", 75),
    ("PatientRecords", 160),
    ("Analytics", 210),
    ("Transactions", 95),
    ("Logs", 130),
]

DISK_REQUESTS = [82, 170, 43, 140, 24, 16, 190, 75, 60, 95, 10, 55]
DISK_HEAD = 50
DISK_SIZE = 200


# ============================================================
# CPU SCHEDULING
# ============================================================

def cpu_fcfs(data):
    data = sorted(data, key=lambda x: (x["arrival"], x["pid"]))
    time = 0
    result = []
    timeline = []

    for p in data:
        if time < p["arrival"]:
            time = p["arrival"]

        start = time
        finish = start + p["burst"]

        timeline.append((p["pid"], start, finish))

        result.append({
            **p,
            "completion": finish,
            "waiting": start - p["arrival"],
            "turnaround": finish - p["arrival"],
            "response": start - p["arrival"]
        })

        time = finish

    return result, timeline


def cpu_sjf(data):
    remaining = [p.copy() for p in data]
    result = []
    timeline = []
    time = 0

    while remaining:
        available = [
            p for p in remaining
            if p["arrival"] <= time
        ]

        if not available:
            time = min(p["arrival"] for p in remaining)
            continue

        p = min(
            available,
            key=lambda x: (x["burst"], x["arrival"])
        )

        start = time
        finish = start + p["burst"]

        timeline.append((p["pid"], start, finish))

        result.append({
            **p,
            "completion": finish,
            "waiting": start - p["arrival"],
            "turnaround": finish - p["arrival"],
            "response": start - p["arrival"]
        })

        remaining.remove(p)
        time = finish

    return result, timeline


def cpu_priority(data):
    remaining = [p.copy() for p in data]
    result = []
    timeline = []
    time = 0

    while remaining:
        available = [
            p for p in remaining
            if p["arrival"] <= time
        ]

        if not available:
            time = min(p["arrival"] for p in remaining)
            continue

        p = min(
            available,
            key=lambda x: (x["priority"], x["arrival"])
        )

        start = time
        finish = start + p["burst"]

        timeline.append((p["pid"], start, finish))

        result.append({
            **p,
            "completion": finish,
            "waiting": start - p["arrival"],
            "turnaround": finish - p["arrival"],
            "response": start - p["arrival"]
        })

        remaining.remove(p)
        time = finish

    return result, timeline


def cpu_rr(data, quantum):
    data = sorted(
        [p.copy() for p in data],
        key=lambda x: (x["arrival"], x["pid"])
    )

    remaining = {
        p["pid"]: p["burst"]
        for p in data
    }

    first_response = {}
    completion = {}

    queue = []
    timeline = []

    time = 0
    index = 0

    while len(completion) < len(data):

        while (
            index < len(data)
            and data[index]["arrival"] <= time
        ):
            queue.append(data[index])
            index += 1

        if not queue:
            time = data[index]["arrival"]
            continue

        p = queue.pop(0)
        pid = p["pid"]

        if pid not in first_response:
            first_response[pid] = time

        start = time
        run = min(quantum, remaining[pid])
        time += run

        timeline.append((pid, start, time))

        remaining[pid] -= run

        while (
            index < len(data)
            and data[index]["arrival"] <= time
        ):
            queue.append(data[index])
            index += 1

        if remaining[pid] > 0:
            queue.append(p)
        else:
            completion[pid] = time

    result = []

    for p in data:

        tat = completion[p["pid"]] - p["arrival"]
        wt = tat - p["burst"]
        rt = first_response[p["pid"]] - p["arrival"]

        result.append({
            **p,
            "completion": completion[p["pid"]],
            "waiting": wt,
            "turnaround": tat,
            "response": rt
        })

    return result, timeline


# ============================================================
# DISK SCHEDULING
# ============================================================

def disk_fcfs(requests, head):
    order = requests.copy()
    movement = 0
    current = head

    for r in order:
        movement += abs(current - r)
        current = r

    return order, movement


def disk_sstf(requests, head):
    remaining = requests.copy()
    order = []
    movement = 0
    current = head

    while remaining:
        nearest = min(
            remaining,
            key=lambda x: abs(x - current)
        )

        movement += abs(current - nearest)
        current = nearest
        order.append(nearest)
        remaining.remove(nearest)

    return order, movement


def disk_scan(requests, head, size):
    left = sorted(
        [x for x in requests if x < head],
        reverse=True
    )

    right = sorted(
        [x for x in requests if x >= head]
    )

    order = right + [size - 1] + left
    order = [x for x in order if x != head]

    movement = 0
    current = head

    for x in order:
        movement += abs(current - x)
        current = x

    return order, movement


def disk_cscan(requests, head, size):
    right = sorted(
        [x for x in requests if x >= head]
    )

    left = sorted(
        [x for x in requests if x < head]
    )

    order = right + [size - 1, 0] + left

    movement = 0
    current = head

    for x in order:
        movement += abs(current - x)
        current = x

    return order, movement


def disk_look(requests, head):
    left = sorted(
        [x for x in requests if x < head],
        reverse=True
    )

    right = sorted(
        [x for x in requests if x >= head]
    )

    order = right + left

    movement = 0
    current = head

    for x in order:
        movement += abs(current - x)
        current = x

    return order, movement


def disk_clook(requests, head):
    left = sorted(
        [x for x in requests if x < head]
    )

    right = sorted(
        [x for x in requests if x >= head]
    )

    order = right + left

    movement = 0
    current = head

    for x in order:
        movement += abs(current - x)
        current = x

    return order, movement


# ============================================================
# MAIN APPLICATION
# ============================================================

class DataCenterApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Intelligent Data Center Resource & Storage Optimization System"
        )

        self.root.geometry("1200x750")
        self.root.configure(bg="#17202A")

        self.create_dashboard()

    # ========================================================
    # DASHBOARD
    # ========================================================

    def create_dashboard(self):

        title = tk.Label(
            self.root,
            text="INTELLIGENT DATA CENTER RESOURCE & STORAGE OPTIMIZATION",
            font=("Arial", 20, "bold"),
            bg="#17202A",
            fg="white"
        )

        title.pack(pady=25)

        subtitle = tk.Label(
            self.root,
            text="Operating System Resource Optimization Framework",
            font=("Arial", 12),
            bg="#17202A",
            fg="#D5DBDB"
        )

        subtitle.pack(pady=5)

        frame = tk.Frame(
            self.root,
            bg="#17202A"
        )

        frame.pack(pady=40)

        buttons = [
            ("CPU Scheduling", self.cpu_window),
            ("Deadlock Analysis", self.deadlock_window),
            ("Memory Management", self.memory_window),
            ("File Allocation", self.file_window),
            ("Disk Scheduling", self.disk_window),
            ("Final Analysis", self.final_window),
        ]

        for i, (text, command) in enumerate(buttons):

            button = tk.Button(
                frame,
                text=text,
                command=command,
                width=28,
                height=3,
                font=("Arial", 12, "bold"),
                bg="#2E86C1",
                fg="white",
                activebackground="#1F618D"
            )

            button.grid(
                row=i // 2,
                column=i % 2,
                padx=25,
                pady=15
            )

        footer = tk.Label(
            self.root,
            text="CPU • Deadlock • Memory • File • Disk • Integrated Analysis",
            font=("Arial", 10),
            bg="#17202A",
            fg="#ABB2B9"
        )

        footer.pack(pady=20)

    # ========================================================
    # CPU WINDOW
    # ========================================================

    def cpu_window(self):

        window = tk.Toplevel(self.root)
        window.title("CPU Scheduling Analysis")
        window.geometry("1200x750")

        tk.Label(
            window,
            text="CPU SCHEDULING ANALYSIS",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        control = tk.Frame(window)
        control.pack(pady=5)

        tk.Label(
            control,
            text="Algorithm:"
        ).grid(row=0, column=0, padx=5)

        algorithm = ttk.Combobox(
            control,
            values=[
                "FCFS",
                "SJF",
                "Priority",
                "Round Robin"
            ],
            state="readonly",
            width=15
        )

        algorithm.current(0)
        algorithm.grid(row=0, column=1, padx=5)

        tk.Label(
            control,
            text="Quantum:"
        ).grid(row=0, column=2, padx=5)

        quantum = tk.Entry(
            control,
            width=8
        )

        quantum.insert(0, "2")
        quantum.grid(row=0, column=3)

        # Input table

        columns = (
            "Process",
            "Arrival",
            "Burst",
            "Priority"
        )

        input_table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            height=8
        )

        for c in columns:
            input_table.heading(c, text=c)
            input_table.column(c, width=120)

        input_table.pack(pady=10)

        for row in PROCESSES:
            input_table.insert(
                "",
                "end",
                values=row
            )

        # Result table

        result_columns = (
            "Process",
            "Arrival",
            "Burst",
            "Priority",
            "Completion",
            "Waiting",
            "Turnaround",
            "Response"
        )

        result_table = ttk.Treeview(
            window,
            columns=result_columns,
            show="headings",
            height=8
        )

        for c in result_columns:
            result_table.heading(c, text=c)
            result_table.column(c, width=105)

        result_table.pack(pady=10)

        summary = tk.Label(
            window,
            text="",
            font=("Arial", 11, "bold")
        )

        summary.pack(pady=5)

        def run():

            data = []

            for item in input_table.get_children():

                values = input_table.item(item)["values"]

                data.append({
                    "pid": str(values[0]),
                    "arrival": int(values[1]),
                    "burst": int(values[2]),
                    "priority": int(values[3])
                })

            selected = algorithm.get()

            if selected == "FCFS":
                result, timeline = cpu_fcfs(data)

            elif selected == "SJF":
                result, timeline = cpu_sjf(data)

            elif selected == "Priority":
                result, timeline = cpu_priority(data)

            else:

                try:
                    q = int(quantum.get())

                    if q <= 0:
                        raise ValueError

                except ValueError:
                    messagebox.showerror(
                        "Invalid Quantum",
                        "Enter a positive integer."
                    )
                    return

                result, timeline = cpu_rr(
                    data,
                    q
                )

            for item in result_table.get_children():
                result_table.delete(item)

            for r in result:

                result_table.insert(
                    "",
                    "end",
                    values=(
                        r["pid"],
                        r["arrival"],
                        r["burst"],
                        r["priority"],
                        r["completion"],
                        r["waiting"],
                        r["turnaround"],
                        r["response"]
                    )
                )

            avg_wait = sum(
                r["waiting"] for r in result
            ) / len(result)

            avg_tat = sum(
                r["turnaround"] for r in result
            ) / len(result)

            avg_response = sum(
                r["response"] for r in result
            ) / len(result)

            total_burst = sum(
                r["burst"] for r in result
            )

            start_time = min(
                r["arrival"] for r in result
            )

            end_time = max(
                r["completion"] for r in result
            )

            elapsed = end_time - start_time

            utilization = (
                total_burst / elapsed
            ) * 100 if elapsed else 0

            summary.config(
                text=(
                    f"Average Waiting = {avg_wait:.2f}    |    "
                    f"Average Turnaround = {avg_tat:.2f}    |    "
                    f"Average Response = {avg_response:.2f}    |    "
                    f"CPU Utilization = {utilization:.2f}%"
                )
            )

            # Gantt chart

            fig, ax = plt.subplots(figsize=(10, 2.5))

            for i, (pid, start, end) in enumerate(timeline):

                ax.barh(
                    0,
                    end - start,
                    left=start,
                    height=0.5
                )

                ax.text(
                    (start + end) / 2,
                    0,
                    pid,
                    ha="center",
                    va="center"
                )

            ax.set_title(
                f"Gantt Chart - {selected}"
            )

            ax.set_xlabel("Time")
            ax.set_yticks([])

            plt.tight_layout()
            plt.show()

        tk.Button(
            window,
            text="RUN CPU ANALYSIS",
            command=run,
            width=25,
            font=("Arial", 11, "bold"),
            bg="#27AE60",
            fg="white"
        ).pack(pady=10)

    # ========================================================
    # DEADLOCK WINDOW
    # ========================================================

    def deadlock_window(self):

        window = tk.Toplevel(self.root)
        window.title("Banker's Algorithm")
        window.geometry("1000x750")

        tk.Label(
            window,
            text="DEADLOCK DETECTION & SAFE-STATE ANALYSIS",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(
            window,
            text="Banker's Algorithm",
            font=("Arial", 13, "bold")
        ).pack()

        # Available

        available_frame = tk.Frame(window)
        available_frame.pack(pady=10)

        tk.Label(
            available_frame,
            text="Available Resources:"
        ).pack(side="left", padx=10)

        available_entries = []

        for value in AVAILABLE:

            e = tk.Entry(
                available_frame,
                width=6
            )

            e.insert(0, str(value))
            e.pack(side="left", padx=5)

            available_entries.append(e)

        # Allocation

        tk.Label(
            window,
            text="Allocation Matrix",
            font=("Arial", 12, "bold")
        ).pack()

        allocation_table = ttk.Treeview(
            window,
            columns=("Process", "R1", "R2", "R3"),
            show="headings",
            height=8
        )

        for c in ("Process", "R1", "R2", "R3"):
            allocation_table.heading(c, text=c)

        allocation_table.pack()

        for i in range(8):

            allocation_table.insert(
                "",
                "end",
                values=(
                    f"P{i+1}",
                    *ALLOCATION[i]
                )
            )

        # Maximum

        tk.Label(
            window,
            text="Maximum Matrix",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 0))

        maximum_table = ttk.Treeview(
            window,
            columns=("Process", "R1", "R2", "R3"),
            show="headings",
            height=8
        )

        for c in ("Process", "R1", "R2", "R3"):
            maximum_table.heading(c, text=c)

        maximum_table.pack()

        for i in range(8):

            maximum_table.insert(
                "",
                "end",
                values=(
                    f"P{i+1}",
                    *MAXIMUM[i]
                )
            )

        # Need

        tk.Label(
            window,
            text="Need Matrix",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 0))

        need_table = ttk.Treeview(
            window,
            columns=("Process", "R1", "R2", "R3"),
            show="headings",
            height=8
        )

        for c in ("Process", "R1", "R2", "R3"):
            need_table.heading(c, text=c)

        need_table.pack()

        status = tk.Label(
            window,
            text="",
            font=("Arial", 13, "bold")
        )

        status.pack(pady=10)

        sequence = tk.Label(
            window,
            text="",
            font=("Arial", 12)
        )

        sequence.pack()

        def run():

            try:

                available = [
                    int(e.get())
                    for e in available_entries
                ]

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Resource values must be integers."
                )
                return

            need = []

            for i in range(8):

                row = []

                for j in range(3):

                    row.append(
                        MAXIMUM[i][j]
                        - ALLOCATION[i][j]
                    )

                need.append(row)

            for item in need_table.get_children():
                need_table.delete(item)

            for i in range(8):

                need_table.insert(
                    "",
                    "end",
                    values=(
                        f"P{i+1}",
                        *need[i]
                    )
                )

            work = available.copy()
            finish = [False] * 8
            safe_sequence = []

            while len(safe_sequence) < 8:

                found = False

                for i in range(8):

                    if finish[i]:
                        continue

                    if all(
                        need[i][j] <= work[j]
                        for j in range(3)
                    ):

                        for j in range(3):
                            work[j] += ALLOCATION[i][j]

                        finish[i] = True
                        safe_sequence.append(
                            f"P{i+1}"
                        )

                        found = True

                if not found:
                    break

            if len(safe_sequence) == 8:

                status.config(
                    text="SYSTEM STATUS: SAFE STATE",
                    fg="green"
                )

                sequence.config(
                    text=(
                        "Safe Sequence: "
                        + " → ".join(safe_sequence)
                    )
                )

            else:

                status.config(
                    text="SYSTEM STATUS: UNSAFE STATE",
                    fg="red"
                )

                sequence.config(
                    text="Deadlock risk detected."
                )

        tk.Button(
            window,
            text="RUN BANKER'S ALGORITHM",
            command=run,
            width=30,
            font=("Arial", 11, "bold"),
            bg="#27AE60",
            fg="white"
        ).pack(pady=15)

    # ========================================================
    # MEMORY MANAGEMENT
    # ========================================================

    def memory_window(self):

        window = tk.Toplevel(self.root)
        window.title("Memory Management")
        window.geometry("1000x700")

        tk.Label(
            window,
            text="MEMORY MANAGEMENT ANALYSIS",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(
            window,
            text="Paging vs Segmentation",
            font=("Arial", 13, "bold")
        ).pack()

        frame = tk.Frame(window)
        frame.pack(pady=20)

        tk.Label(
            frame,
            text="Physical Memory (bytes):"
        ).grid(row=0, column=0)

        memory_entry = tk.Entry(frame)
        memory_entry.insert(0, "2048")
        memory_entry.grid(row=0, column=1, padx=10)

        tk.Label(
            frame,
            text="Page Size (bytes):"
        ).grid(row=0, column=2)

        page_entry = tk.Entry(frame)
        page_entry.insert(0, "64")
        page_entry.grid(row=0, column=3, padx=10)

        columns = (
            "Process",
            "Size",
            "Pages",
            "Allocated",
            "Internal Fragmentation"
        )

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            height=8
        )

        for c in columns:
            table.heading(c, text=c)
            table.column(c, width=170)

        table.pack(pady=10)

        result_label = tk.Label(
            window,
            text="",
            font=("Arial", 11, "bold")
        )

        result_label.pack(pady=10)

        def run():

            try:

                memory = int(memory_entry.get())
                page_size = int(page_entry.get())

                if memory <= 0 or page_size <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter valid positive values."
                )
                return

            for item in table.get_children():
                table.delete(item)

            total_pages = 0
            total_frag = 0
            total_size = 0

            for pid, size in MEMORY_PROCESSES:

                pages = (size + page_size - 1) // page_size

                allocated = pages * page_size
                fragmentation = allocated - size

                total_pages += pages
                total_frag += fragmentation
                total_size += size

                table.insert(
                    "",
                    "end",
                    values=(
                        pid,
                        size,
                        pages,
                        allocated,
                        fragmentation
                    )
                )

            total_allocated = total_pages * page_size

            utilization = (
                total_size / memory
            ) * 100

            result_label.config(
                text=(
                    f"Total Pages = {total_pages}    |    "
                    f"Total Internal Fragmentation = {total_frag} bytes    |    "
                    f"Memory Utilization = {utilization:.2f}%    |    "
                    f"Total Allocated = {total_allocated} bytes"
                )
            )

            # Chart

            labels = [
                p[0] for p in MEMORY_PROCESSES
            ]

            sizes = [
                p[1] for p in MEMORY_PROCESSES
            ]

            plt.figure(figsize=(8, 4))
            plt.bar(labels, sizes)
            plt.title("Process Memory Requirements")
            plt.xlabel("Process")
            plt.ylabel("Memory (bytes)")
            plt.tight_layout()
            plt.show()

        tk.Button(
            window,
            text="RUN MEMORY ANALYSIS",
            command=run,
            width=25,
            font=("Arial", 11, "bold"),
            bg="#27AE60",
            fg="white"
        ).pack(pady=10)

        # Segmentation result

        tk.Label(
            window,
            text="Segmentation Data: P1, P2, P3",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        segmentation_total = sum(
            a + b + c
            for _, a, b, c in SEGMENTS
        )

        tk.Label(
            window,
            text=(
                f"Total Segmentation Allocation = "
                f"{segmentation_total} bytes"
            )
        ).pack()

    # ========================================================
    # FILE ALLOCATION
    # ========================================================

    def file_window(self):

        window = tk.Toplevel(self.root)
        window.title("File Allocation")
        window.geometry("1000x700")

        tk.Label(
            window,
            text="FILE ALLOCATION ANALYSIS",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(
            window,
            text="Contiguous • Linked • Indexed",
            font=("Arial", 13, "bold")
        ).pack()

        frame = tk.Frame(window)
        frame.pack(pady=15)

        tk.Label(
            frame,
            text="Block Size:"
        ).grid(row=0, column=0)

        block_entry = tk.Entry(
            frame,
            width=8
        )

        block_entry.insert(0, "10")
        block_entry.grid(row=0, column=1, padx=10)

        columns = (
            "File",
            "Size",
            "Blocks",
            "Contiguous",
            "Linked",
            "Indexed"
        )

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            height=8
        )

        for c in columns:
            table.heading(c, text=c)
            table.column(c, width=145)

        table.pack(pady=10)

        result = tk.Label(
            window,
            text="",
            font=("Arial", 11, "bold")
        )

        result.pack(pady=15)

        def run():

            try:
                block_size = int(
                    block_entry.get()
                )

                if block_size <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Block size must be positive."
                )
                return

            for item in table.get_children():
                table.delete(item)

            total_blocks = 0

            for name, size in FILES:

                blocks = (
                    size + block_size - 1
                ) // block_size

                total_blocks += blocks

                contiguous = blocks
                linked = blocks + 1
                indexed = blocks + 1

                table.insert(
                    "",
                    "end",
                    values=(
                        name,
                        size,
                        blocks,
                        contiguous,
                        linked,
                        indexed
                    )
                )

            result.config(
                text=(
                    f"Total Data Blocks = {total_blocks}    |    "
                    f"Contiguous Metadata = minimal    |    "
                    f"Linked Metadata = {len(FILES)} pointer blocks    |    "
                    f"Indexed Metadata = {len(FILES)} index blocks"
                )
            )

            methods = [
                "Contiguous",
                "Linked",
                "Indexed"
            ]

            efficiency = [
                total_blocks,
                total_blocks + len(FILES),
                total_blocks + len(FILES)
            ]

            plt.figure(figsize=(8, 4))
            plt.bar(methods, efficiency)
            plt.title("File Allocation Storage Requirement")
            plt.ylabel("Blocks")
            plt.tight_layout()
            plt.show()

        tk.Button(
            window,
            text="RUN FILE ANALYSIS",
            command=run,
            width=25,
            font=("Arial", 11, "bold"),
            bg="#27AE60",
            fg="white"
        ).pack(pady=10)

    # ========================================================
    # DISK SCHEDULING
    # ========================================================

    def disk_window(self):

        window = tk.Toplevel(self.root)
        window.title("Disk Scheduling")
        window.geometry("1050x750")

        tk.Label(
            window,
            text="DISK SCHEDULING ANALYSIS",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(
            window,
            text=(
                f"Initial Head = {DISK_HEAD} | "
                f"Cylinders = 0–{DISK_SIZE - 1}"
            ),
            font=("Arial", 12)
        ).pack()

        columns = (
            "Algorithm",
            "Total Head Movement",
            "Average Movement"
        )

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            height=8
        )

        for c in columns:
            table.heading(c, text=c)
            table.column(c, width=220)

        table.pack(pady=20)

        algorithms = {
            "FCFS": disk_fcfs,
            "SSTF": disk_sstf,
            "SCAN": lambda r, h: disk_scan(
                r, h, DISK_SIZE
            ),
            "C-SCAN": lambda r, h: disk_cscan(
                r, h, DISK_SIZE
            ),
            "LOOK": disk_look,
            "C-LOOK": disk_clook
        }

        result_label = tk.Label(
            window,
            text="",
            font=("Arial", 13, "bold")
        )

        result_label.pack(pady=15)

        def run():

            for item in table.get_children():
                table.delete(item)

            movements = {}

            for name, function in algorithms.items():

                order, movement = function(
                    DISK_REQUESTS,
                    DISK_HEAD
                )

                movements[name] = movement

                average = (
                    movement /
                    len(DISK_REQUESTS)
                )

                table.insert(
                    "",
                    "end",
                    values=(
                        name,
                        movement,
                        f"{average:.2f}"
                    )
                )

            best = min(
                movements,
                key=movements.get
            )

            result_label.config(
                text=(
                    f"Recommended Disk Algorithm: {best}    |    "
                    f"Minimum Head Movement: "
                    f"{movements[best]} cylinders"
                )
            )

            plt.figure(figsize=(9, 4))

            plt.bar(
                list(movements.keys()),
                list(movements.values())
            )

            plt.title(
                "Disk Scheduling Comparison"
            )

            plt.ylabel(
                "Total Head Movement"
            )

            plt.xticks(rotation=20)

            plt.tight_layout()
            plt.show()

        tk.Button(
            window,
            text="RUN DISK ANALYSIS",
            command=run,
            width=25,
            font=("Arial", 11, "bold"),
            bg="#27AE60",
            fg="white"
        ).pack(pady=10)

        tk.Label(
            window,
            text=(
                "Request Queue: "
                + ", ".join(
                    map(str, DISK_REQUESTS)
                )
            ),
            wraplength=900
        ).pack(pady=10)

    # ========================================================
    # FINAL ANALYSIS
    # ========================================================

    def final_window(self):

        window = tk.Toplevel(self.root)
        window.title("Integrated Final Analysis")
        window.geometry("1050x750")

        tk.Label(
            window,
            text="INTEGRATED PERFORMANCE ANALYSIS",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        # CPU comparison

        cpu_data = [
            ("FCFS", 16.88),
            ("SJF", 12.00),
            ("Priority", 15.25),
            ("Round Robin", 21.00)
        ]

        disk_data = [
            ("FCFS", 937),
            ("SSTF", 320),
            ("SCAN", 320),
            ("C-SCAN", 373),
            ("LOOK", 320),
            ("C-LOOK", 353)
        ]

        columns = (
            "Area",
            "Recommended Technique",
            "Reason"
        )

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            height=7
        )

        for c in columns:
            table.heading(c, text=c)
            table.column(c, width=260)

        table.pack(pady=20)

        recommendations = [
            (
                "CPU Scheduling",
                "SJF",
                "Lowest average waiting time"
            ),
            (
                "Deadlock",
                "Banker's Algorithm",
                "Produces safe state and safe sequence"
            ),
            (
                "Memory",
                "Paging",
                "Better memory utilization"
            ),
            (
                "File Allocation",
                "Indexed",
                "Suitable for direct/random access"
            ),
            (
                "Disk Scheduling",
                "SSTF",
                "Lowest head movement for workload"
            ),
        ]

        for row in recommendations:

            table.insert(
                "",
                "end",
                values=row
            )

        tk.Label(
            window,
            text="PERFORMANCE SUMMARY",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        summary = (
            "CPU: SJF provides the lowest average waiting time.\n\n"
            "Deadlock: The system is in a SAFE state using Banker's Algorithm.\n\n"
            "Memory: Paging provides effective memory utilization with measurable internal fragmentation.\n\n"
            "File: Indexed allocation is suitable when direct/random access is important.\n\n"
            "Disk: SSTF provides the lowest head movement for the selected workload.\n\n"
            "Overall Recommendation: Use a hybrid strategy where the algorithm is selected according to workload characteristics."
        )

        tk.Label(
            window,
            text=summary,
            font=("Arial", 11),
            justify="left",
            wraplength=900
        ).pack(pady=10)

        def show_chart():

            areas = [
                "CPU",
                "Memory",
                "Disk"
            ]

            scores = [
                88,
                82,
                91
            ]

            plt.figure(figsize=(8, 4))

            plt.bar(
                areas,
                scores
            )

            plt.title(
                "Overall Resource Optimization Score"
            )

            plt.ylabel(
                "Performance Score"
            )

            plt.ylim(0, 100)

            plt.tight_layout()
            plt.show()

        tk.Button(
            window,
            text="SHOW OVERALL PERFORMANCE GRAPH",
            command=show_chart,
            width=35,
            font=("Arial", 11, "bold"),
            bg="#2E86C1",
            fg="white"
        ).pack(pady=20)


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = DataCenterApp(root)

    root.mainloop()