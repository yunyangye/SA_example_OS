# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

#start the measure
class ReplaceLightsInSpaceTypeWithLPD < OpenStudio::Ruleset::ModelUserScript

  #define the name that a user will see
  def name
    return "Replace Lights in Space Type with LPD"
  end

  # human readable description
  def description
    return "This measure aims to change LPD."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Modify the value of LPD."
  end  
  
  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new

    #make an argument for LPD
    lpd = OpenStudio::Ruleset::OSArgument::makeDoubleArgument('lpd',true)
    lpd.setDisplayName('Lighting Power Density (W/m^2)')
    lpd.setDefaultValue(1.0)
    args << lpd

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
    lpd = runner.getDoubleArgumentValue('lpd',user_arguments)

   #check the LPD for reasonableness
    if lpd < 0 or lpd > 100 #error on impossible values
      runner.registerError("Lighting Power Density (W/m^2) must be
                              greater than 0 and less than 100.
                              You entered #{lpd}.")
      return false
    elsif lpd > 50 #warning on unrealistic but possible values
      runner.registerWarning("A Lighting Power Density of #{lpd} W/m^2
                              seems a little high.  Measure will continue,
                              but double-check this isn't a typo.")
    end

    #create a variable and array for tracking changes to model
    num_spctyp_changed = 0
    spctyp_ch_log = []

    #make changes to the model
    #loop through all space types in the model
    model.getSpaceTypes.each do |space_type|
      num_spctyp_changed += 1 #log change
      runner.registerInfo("Space Type called #{space_type.name}.")
      #loop through all lights in the space type
      space_type.lights.each do |light|
        #get the old lpd from the existing lights definition, if exists
        old_lpd = "not per-area"
        if not light.lightsDefinition.wattsperSpaceFloorArea.empty?
          old_lpd = light.lightsDefinition.wattsperSpaceFloorArea.get
        end
        #add the old and new condition to the change log
        spctyp_ch_log << [space_type.name, old_lpd]
        #make a new lights definition
        new_lights_def = OpenStudio::Model::LightsDefinition.new(model)
        new_lights_def.setWattsperSpaceFloorArea(lpd)
        new_lights_def.setName("#{lpd} W/m^2 Lights Definition")
        #replace the old lights def with the new lights def
        light.setLightsDefinition(new_lights_def)
      end
    end

    #report out the initial and final condition to the user
    initial_condition = ""
    initial_condition << "There are #{num_spctyp_changed} space types."
    final_condition = ""
    spctyp_ch_log.each do |ch|
      initial_condition << "Space type #{ch[0]} had an lpd of #{ch[1]}
                            W/m^2. "
      final_condition << "space type #{ch[0]}, "
    end
    final_condition << "were all set to an lpd of #{lpd} W/m^2"
    runner.registerInitialCondition(initial_condition)
    runner.registerFinalCondition(final_condition)

    #report if the measure was Not Applicable
    if num_spctyp_changed == 0
      runner.registerAsNotApplicable("Not Applicable.")
    end

    return true
  end #end the run method

end #end the measure

#boilerplate that allows the measure to be use by the application
ReplaceLightsInSpaceTypeWithLPD.new.registerWithApplication