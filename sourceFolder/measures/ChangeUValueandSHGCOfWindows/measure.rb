#This measure created by Yunyang Ye
#This measure can change u-value and shgc of windows simultaneously

#start the measure
class ChangeUValueandSHGCOfWindows < OpenStudio::Ruleset::ModelUserScript

  #define the name that a user will see
  def name
    return "Change U-Value and SHGC Of Windows"
  end

  # human readable description
  def description
    return "This measure aims to change U-Value and SHGC of windows."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Change U-Value and SHGC of windows."
  end  
  
  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new
    
    window_u_value_ip = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("window_u_value_ip",true)
    window_u_value_ip.setDisplayName("Window U-Value (Btu/ft^2*h*R)")
    window_u_value_ip.setDefaultValue(10.0)
    args << window_u_value_ip

    window_shgc = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("window_shgc",true)
    window_shgc.setDisplayName("Window SHGC")
    window_shgc.setDefaultValue(0.5)
    args << window_shgc	
	
    return args
  end #end the arguments method

  #define what happens when the measure is run
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)

    #use the built-in error checking
    if not runner.validateUserArguments(arguments(model), user_arguments)
      return false
    end   
    
    #assign the user inputs to variables
    window_u_value_ip = runner.getDoubleArgumentValue("window_u_value_ip",user_arguments)
    window_shgc = runner.getDoubleArgumentValue("window_shgc",user_arguments)
	
    # Convert U-Value to SI units
    window_u_value_si = OpenStudio.convert(window_u_value_ip, "Btu/ft^2*h*R","W/m^2*K").get

    # Create the new window construction
    window_material = OpenStudio::Model::SimpleGlazing.new(model)
    window_material.setName("Simple Glazing Material U-#{window_u_value_ip} and SHGC #{window_shgc}")
    window_material.setUFactor(window_u_value_si)
    window_material.setSolarHeatGainCoefficient(window_shgc)
    window_construction = OpenStudio::Model::Construction.new(model)
    window_construction.setName("Window U-#{window_u_value_ip} and Window SHGC #{window_shgc}")
    window_construction.insertLayer(0, window_material)
     
    # loop through sub surfaces and hard-assign
    # new window construction.
    total_area_changed_si = 0
    model.getSubSurfaces.each do |sub_surface|
      if sub_surface.outsideBoundaryCondition == "Outdoors" && (sub_surface.subSurfaceType == "FixedWindow" || sub_surface.subSurfaceType == "OperableWindow")
        sub_surface.setConstruction(window_construction)
        total_area_changed_si += sub_surface.grossArea
      end
    end
    
    total_area_changed_ip = OpenStudio.convert(total_area_changed_si, "m^2", "ft^2").get
    runner.registerFinalCondition("Changed #{total_area_changed_ip.round} ft2 of windows to U-#{window_u_value_ip.round(1)} and SHGC = #{window_shgc}")
    
    return true

  end #end the run method

end #end the measure

#this allows the measure to be used by the application
ChangeUValueandSHGCOfWindows.new.registerWithApplication