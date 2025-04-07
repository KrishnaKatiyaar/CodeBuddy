import cProfile
import pstats
import io
import matplotlib.pyplot as plt

def profile_code(code_to_profile):
    pr = cProfile.Profile()
    pr.enable()
    try:
        exec(code_to_profile, {}, {})
    except Exception as e:
        return {"error": f"Execution error: {str(e)}"}
    pr.disable()
    stream = io.StringIO()
    ps = pstats.Stats(pr, stream=stream)
    ps.strip_dirs().sort_stats("cumulative").print_stats()
    return stream.getvalue().strip()

def visualize_hotspots(profile_data):
    try:
        lines = profile_data.split("\n")
        function_data = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 6 and parts[0].isdigit():
                time_taken = float(parts[2])
                function_name = " ".join(parts[5:])
                function_data.append((function_name, time_taken))
        
        if not function_data:
            return {"error": "No function execution data found"}
            
        function_data.sort(key=lambda x: x[1], reverse=True)
        function_names = [f[0] for f in function_data[:10]]
        times = [f[1] for f in function_data[:10]]
        
        plt.figure(figsize=(10, 6))
        plt.barh(function_names, times, color='skyblue')
        plt.xlabel("Execution Time (Seconds)")
        plt.ylabel("Function Name")
        plt.title("Code Hotspot Visualization")
        plt.gca().invert_yaxis()
        
        plt.savefig("hotspot_plot.png", bbox_inches="tight")
        plt.close()
        
        return {"message": "Hotspot visualization generated", "image_path": "hotspot_plot.png"}
    except Exception as e:
        return {"error": f"Visualization error: {str(e)}"} 