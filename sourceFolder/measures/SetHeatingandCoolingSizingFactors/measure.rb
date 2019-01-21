# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

#start the measure
class SetHeatingandCoolingSizingFactors < OpenStudio::Ruleset::ModelUserScript
  
  #define the name that a user will see, this method may be deprecated as
  #the display name in PAT comes from the name field in measure.xml
  def name
    return "Set Heating and Cooling Sizing Factors"
  end

  #human readable description
  def description
    return "This measure aims to resize heating and cooling sizes."
  end

  #human readable description of modeling approach
  def modeler_description
    return "Resize heating and cooling sizes."
  end  
  
  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new
    
    #make an argument to add heating sizing factor
    htg_sz_factor = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("htg_sz_factor",true)
    htg_sz_factor.setDisplayName("Heating Sizing Factor (eg 1.25 = 125% of required heating capacity.")
    htg_sz_factor.setDefaultValue(1.25)
    args << htg_sz_factor
    
    #make an argument to add cooling sizing factor
    clg_sz_factor = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("clg_sz_factor",true)
    clg_sz_factor.setDisplayName("Coolinig Sizing Factor (eg 1.15 = 115% of required cooling capacity.")
    clg_sz_factor.setDefaultValue(1.15)
    args << clg_sz_factor    
    
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
    htg_sz_factor = runner.getDoubleArgumentValue("htg_sz_factor",user_arguments)
    clg_sz_factor = runner.getDoubleArgumentValue("clg_sz_factor",user_arguments)
    
    #get the existing sizing parameters or make a new one as required
    siz_params = model.getSimulationControl.sizingParameters
    if siz_params.is_initialized
      siz_params = siz_params.get
    else
      siz_params_idf = OpenStudio::IdfObject.new OpenStudio::Model::SizingParameters::iddObjectType
      model.addObject siz_params_idf
      siz_params = model.getSimulationControl.sizingParameters.get
    end

    #report the initial condition
    orig_htg_sz_factor = siz_params.heatingSizingFactor
    orig_clg_sz_factor = siz_params.coolingSizingFactor
    runner.registerInitialCondition("Model started with htg sizing factor = #{orig_htg_sz_factor} and clg sizing factor = #{orig_clg_sz_factor}")    
    
    #set the sizing factors to the user specified values
    siz_params.setHeatingSizingFactor(htg_sz_factor)
    siz_params.setCoolingSizingFactor(clg_sz_factor)

    #report the final condition
    new_htg_sz_factor = siz_params.heatingSizingFactor
    new_clg_sz_factor = siz_params.coolingSizingFactor
    runner.registerFinalCondition("Model ended with htg sizing factor = #{new_htg_sz_factor} and clg sizing factor = #{new_clg_sz_factor}")  
  
    return true
 
  end #end the run method

end #end the measure

#this allows the measure to be use by the application
SetHeatingandCoolingSizingFactors.new.registerWithApplication