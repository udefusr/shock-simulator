
#### *Early project concept (up for discussion)*

## A small simulation project about what happens when a major shock hits a connected system. The main idea is to let us create a scenario, watch the effects build up over time and compare different responses.


# **1\. The Basic Idea**

The project would model a real-world system that depends on several connected parts. A sudden event, for example oil disruption, a major flood, a port closure or a power failure. These would affect one or more of those parts. The simulator would then follow the knock-on effects.

We are not trying to build a tool that can perfectly predict a war, disaster or the economy. The point is to build a useful model and see what happens under a set of assumptions and randomness.

# **2\. What is the main focus?**

Main focus: understanding the impact of a shock and testing possible responses by showing our ball knowledge.

The project can roughly follow this:

| Starting State | Shock | Impact | Critical Point | Response |
| :---- | :---- | :---- | :---- | :---- |

**For example**: The system starts with a certain amount of supply and reserves \-\> supply suddenly drops \-\> other dependent areas are affected \-\> a chosen risk threshold is reached \-\> we test a response and see whether the situation improves.

# **3\. Possible first use case: energy / oil shock**

This is one possible direction, not a final decision. It is interesting because energy systems are highly connected: supply, imports, reserves, transport and electricity can affect one another.

* A major source of supply is reduced or unavailable.  
* The simulator shows how that shortage changes the rest of the system over time  
* We define a few simple thresholds that represent a serious situation.  
* We test what happens when different measures are introduced, such as using reserves or reducing demand.

# **4\. What would the user actually see?**

The final version could have a simple interactive screen rather than a complicated control room. The user chooses a scenario and sees a few useful numbers and graphs.  
    • Current state of the system  
    • Size and duration of the shock  
    • How the situation changes over time  
    • Which thresholds have been crossed or are approaching  
    • The result of different response options  
	 		

# **5\. How could we build it?**

For the first version, it probably makes more sense to build this as a normal software project, not a game. The simulation itself can stay separate from whatever interface we use, so the model can be changed without rebuilding the whole project.  
	

| Part | Likely tool | Why  |
| :---- | :---- | :---- |
| 				Simulation / calculations 			 | 				Python \+ NumPy 			 | Easy to change the model and run many scenarios. |
| 				Data handling 			 | 				Python \+ Pandas 			 | Useful for historical or current datasets. |
| 				Network / dependencies 			 | 				NetworkX (if needed) 			 | Makes it easier to represent connected parts of a system. |
| 				Charts / dashboard 			 | 				Plotly \+ Streamlit 			 | Fast way to make an interactive web-style interface. |
| 				Optional visual version 			 | 				Godot 			 | Only if we later want a map-like or more visual simulation. |

Godot would be optional rather than the starting point. Most of the work is in the simulation and the data. If we later decide that a map or a more visual presentation would make the project better, Godot could be used for that layer.  
	 	

# **6\. A realistic first version**

To keep this manageable, the first version should be much smaller than the final idea:

* Choose one scenario.  
* Use a small number of variables.  
* Create a basic time-based simulation.  
* Add one or two critical thresholds.  
* Add a simple chart showing the situation over time.  
* Test one or two mitigation strategies.

Once that works, we can decide whether the project is worth expanding with better data, more detailed dependencies, forecasting, optimization, or a more advanced interface.

# **7\. Things we still need to decide**

* What kind of shock should be the main example?   
* Should the first version focus on energy, disaster response, supply chains, or something else?  
* How realistic does the model need to be?  
* Which datasets are actually 	available and reliable enough to use?   
* Which thresholds make sense for the chosen problem?  
* Do we want forecasting and 	optimization to be central features or just later additions?