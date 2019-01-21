# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

# start the measure
class SetWaterHeaterEfficiency < OpenStudio::Ruleset::ModelUserScript

  # human readable name
  def name
    return "Set Water Heater Efficiency"
  end

  # human readable description
  def description
    return "This measure aims to change water heater efficiency and fuel type."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Change water heater efficiency and fuel type."
  end

  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new
   
    #make a choice argument for economizer control type	
	heater_fuel_type_handles = OpenStudio::StringVector.new
	heater_fuel_type_display_names = OpenStudio::StringVector.new
	
	fuel_type_array = ["NaturalGas","Electricity","PropaneGas","FuelOil#1","FuelOil#2",\
		"Coal","Diesel","Gasoline","OtherFuel1","OtherFuel2","Steam","DistrictHeating"]

	for i in 0..fuel_type_array.size-1
		heater_fuel_type_handles << i.to_s	
		heater_fuel_type_display_names << fuel_type_array[i]
	end
	
    #make a choice argument for economizer control type
    heater_fuel_type_widget = OpenStudio::Ruleset::OSArgument::makeChoiceArgument("heater_fuel_type_widget", heater_fuel_type_handles, heater_fuel_type_display_names,true)
    heater_fuel_type_widget.setDisplayName("Fuel type")
	heater_fuel_type_widget.setDefaultValue(heater_fuel_type_display_names[0])	
    args << heater_fuel_type_widget

	#make an argument for heater Thermal Efficiency (default of 0.8)
	heater_thermal_efficiency = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("heater_thermal_efficiency", true)
    heater_thermal_efficiency.setDisplayName("Thermal efficiency [between 0 and 1]")
    heater_thermal_efficiency.setDefaultValue(0.8)
    args << heater_thermal_efficiency
	
    return args
  end #end the arguments method

  #define what happens when the measure is run
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)
    
    #use the built-in error checking 
    if not runner.validateUserArguments(arguments(model), user_arguments)
      return false
    end
	
	fuel_type_array = ['NaturalGas','Electricity','PropaneGas','FuelOil#1','FuelOil#2',\
		'Coal','Diesel','Gasoline','OtherFuel1','OtherFuel2','Steam','DistrictHeating']
	
	handle = runner.getStringArgumentValue("heater_fuel_type_widget",user_arguments)
	heater_fuel_type = handle.to_i
	heater_fuel = fuel_type_array[heater_fuel_type]

	heater_thermal_efficiency = runner.getDoubleArgumentValue("heater_thermal_efficiency",user_arguments)
	
	if heater_thermal_efficiency <= 0 
		runner.registerError("Enter a value greater than zero for the 'Heater Thermal Efficiency'.")
	elsif heater_thermal_efficiency > 1.0 
		runner.registerError("Enter a value less than or equal to 1.0 for the 'HeaterThermal Efficiency'.")
	end
	
	i_water_heater = 0
	model.getWaterHeaterMixeds.each do |water_heater|
		i_water_heater = i_water_heater + 1
		
		# check if AllAirloop is selected or not.
		unit = water_heater.to_WaterHeaterMixed.get
			
		#get the original value for reporting
		heater_thermal_efficiency_old = unit.heaterThermalEfficiency
		oncycle_loss_coeff_old = unit.onCycleLossCoefficienttoAmbientTemperature
		offcycle_loss_coeff_old = unit.offCycleLossCoefficienttoAmbientTemperature
		peak_use_flow_old = unit.peakUseFlowRate
			
		runner.registerInfo("Initial: Heater Thermal Efficiency of '#{unit.name}' was #{heater_thermal_efficiency_old}.")
		runner.registerInfo("Initial: On Cycle Loss Coefficient to Ambient Temperature of '#{unit.name}' was #{oncycle_loss_coeff_old}.")
		runner.registerInfo("Initial: Off Cycle Loss Coefficient to Ambient Temperature'#{unit.name}' was #{offcycle_loss_coeff_old}.")
		if peak_use_flow_old.is_a? Numeric	
			runner.registerInfo("Initial: Peak Use Flow Rate of '#{unit.name}' was #{peak_use_flow_old}.")
		end
					
		#now we have all user inputs, so set them to the new model
		unit.setHeaterFuelType(heater_fuel)
		unit.setHeaterThermalEfficiency(heater_thermal_efficiency)
			
		runner.registerInfo("Final: Heater Thermal Efficiency of '#{unit.name}' was set to be #{heater_thermal_efficiency}.")				
	end

    return true
  
  end #end the run method

end #end the measure

# register the measure to be used by the application
SetWaterHeaterEfficiency.new.registerWithApplication
