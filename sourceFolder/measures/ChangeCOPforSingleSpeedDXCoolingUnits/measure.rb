# see the URL below for information on how to write OpenStudio measures
# http://openstudio.nrel.gov/openstudio-measure-writing-guide

# start the measure
class ChangeCOPforSingleSpeedDXCoolingUnits < OpenStudio::Ruleset::ModelUserScript

  # human readable name
  def name
    return "Change COP for Single Speed DX Cooling Units"
  end

  # human readable description
  def description
    return "This measure aims to use percentage of COP's change to modify the value COP."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Modify the percentage of change of COP, and the value can be -100~100. If value < 0, it means the value is decreased."
  end

  # define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new
    
    # Make an argument for the percent COP increase
    cop = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("cop",true)
    cop.setDisplayName("COP")
    cop.setDefaultValue(3.0)
    args << cop

    return args
  end

  # define what happens when the measure is run
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)

    # use the built-in error checking
    if !runner.validateUserArguments(arguments(model), user_arguments)
      return false
    end

    cop = runner.getDoubleArgumentValue("cop",user_arguments)   
    
    # Check arguments for reasonableness
    if cop <= 0 || cop >= 10 
      runner.registerError("COP must be between 0 and 10")
      return false
    end

    # Loop through all single speed and two speed DX coils
    # and increase their COP by the specified percentage 
    # to reflect higher efficiency compressor motors.
    dx_coils = []
    
    # Two Speed DX Coils
    model.getCoilCoolingDXTwoSpeeds.each do |dx_coil|
      dx_coils << dx_coil
      # Change the high speed COP
      initial_high_cop = dx_coil.ratedHighSpeedCOP
      if initial_high_cop.is_initialized
        initial_high_cop = initial_high_cop.get
        new_high_cop = cop
        dx_coil.setRatedHighSpeedCOP(new_high_cop)
        runner.registerInfo("Increased the high speed COP of #{dx_coil.name} from #{initial_high_cop} to #{new_high_cop}.")
      end
      # Change the low speed COP
      initial_low_cop = dx_coil.ratedLowSpeedCOP
      if initial_low_cop.is_initialized
        initial_low_cop = initial_low_cop.get
        new_low_cop = cop
        dx_coil.setRatedLowSpeedCOP(new_low_cop)
        runner.registerInfo("Increased the low speed COP of #{dx_coil.name} from #{initial_low_cop} to #{new_low_cop}.")
      end
    end  
          
    # Single Speed DX Coils
    model.getCoilCoolingDXSingleSpeeds.each do |dx_coil|
      dx_coils << dx_coil
      # Change the COP
      initial_cop = dx_coil.ratedCOP
      if initial_cop.is_initialized
        initial_cop = initial_cop.get
        new_cop = OpenStudio::OptionalDouble.new(cop)
        dx_coil.setRatedCOP(new_cop)
        runner.registerInfo("Increased the COP of #{dx_coil.name} from #{initial_cop} to #{new_cop}.")
      end
    end
    
    # Not applicable if no dx coils
    if dx_coils.size == 0
      runner.registerAsNotApplicable("This measure is not applicable because there were no DX cooling coils in the building.")
      return true    
    end

    # Report final condition
    runner.registerFinalCondition("Increased the COP in #{dx_coils.size} DX cooling coils by #{cop} to reflect the efficiency of Brushless DC Motors.")

    return true

  end
  
end

# register the measure to be used by the application
ChangeCOPforSingleSpeedDXCoolingUnits.new.registerWithApplication