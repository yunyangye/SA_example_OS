# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

# start the measure
class SetGasBurnerEfficiency < OpenStudio::Ruleset::ModelUserScript

  # human readable name
  def name
    return "Set Gas Burner Efficiency"
  end

  # human readable description
  def description
    return "This measure aims to change gas burner efficiency."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Change gas burner efficiency."
  end

  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new

    #make an argument to add new space true/false
    eff = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("eff",true)
    eff.setDisplayName("Burner Efficiency (fractional)")
    eff.setDefaultValue(0.95)
    args << eff

    return args
  end #end the arguments method

  #define what happens when the measure is eff
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)

    #use the built-in error checking
    if not runner.validateUserArguments(arguments(model), user_arguments)
      return false
    end

    #assign the user inputs to variables
    eff = runner.getDoubleArgumentValue("eff",user_arguments)

    #check the user_name for reasonableness
    if eff <= 0
      runner.registerError("Please enter a positive value no greater tan 1 for burner efficiency.")
      return false
    end
    if eff > 1
      runner.registerError("Please enter a positive value no greater tan 1 for burner efficiency.")
      return false
    end
    if eff > 0.99
      runner.registerWarning("The requested burner efficiency of #{eff} seems unusually high")
    end

    #short def to make numbers pretty (converts 4125001.25641 to 4,125,001.26 or 4,125,001). The definition be called through this measure
    def neat_numbers(number, roundto = 2) #round to 0 or 2)
      if roundto == 2
        number = sprintf "%.2f", number
      else
        number = number.round
      end
      #regex to add commas
      number.to_s.reverse.gsub(%r{([0-9]{3}(?=([0-9])))}, "\\1,").reverse
    end #end def neat_numbers

    #get air loops for measure
    air_loops = model.getAirLoopHVACs

    # get eff values
    initial_eff_values = []

    #loop through air loops
    air_loops.each do |air_loop|
      supply_components = air_loop.supplyComponents

      #find two speed dx units on loop
      supply_components.each do |supply_component|
        hVACComponent = supply_component.to_CoilHeatingGas
        if not hVACComponent.empty?
          hVACComponent = hVACComponent.get

          #change and report high speed eff
          initial_eff = hVACComponent.gasBurnerEfficiency
          initial_eff_values << initial_eff
          runner.registerInfo("Changing the burner efficiency from #{initial_eff} to #{eff} for gas heating units '#{hVACComponent.name}' on air loop '#{air_loop.name}'")
          hVACComponent.setGasBurnerEfficiency(eff)

        end #end if not hVACComponent.empty?

      end #end supply_components.each do

    end #end air_loops.each do

    #reporting initial condition of model
    runner.registerInitialCondition("The starting efficiency values in affected loop(s) range from #{initial_eff_values.min} to #{initial_eff_values.max}.")

    if initial_eff_values.size == 0
      runner.registerAsNotApplicable("The affected loop(s) does not contain any Coil Heating Gas units, the model will not be altered.")
      return true
    end

    #reporting final condition of model
    runner.registerFinalCondition("#{initial_eff_values.size} Coil Heating Gas units had their Rated COP values set to #{eff}.")

    return true

  end #end the eff method

end #end the measure

# register the measure to be used by the application
SetGasBurnerEfficiency.new.registerWithApplication
