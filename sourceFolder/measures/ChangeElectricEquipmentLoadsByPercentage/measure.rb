# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

#start the measure
class ChangeElectricEquipmentLoadsByPercentage < OpenStudio::Ruleset::ModelUserScript

  #define the name that a user will see
  def name
    return "Change Electric Equipment Loads by Percentage"
  end

  #human readable description
  def description
    return "This measure aims to change electric equipment loads."
  end

  #human readable description of modeling approach
  def modeler_description
    return "Modify electric equipment loads by percentage."
  end  
  
  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new
	
    #make an argument for changed percentage
    elecequip_power_change_percent = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("elecequip_power_change_percent",true)
    elecequip_power_change_percent.setDisplayName("Electric Equipment Power changes (%).")
    elecequip_power_change_percent.setDefaultValue(30.0)
    args << elecequip_power_change_percent
	
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
    elecequip_power_change_percent = runner.getDoubleArgumentValue("elecequip_power_change_percent",user_arguments)
	
    #check the elecequip_power_change_percent and for reasonableness
    if elecequip_power_change_percent > 100 or elecequip_power_change_percent < -1000
      runner.registerError("Please Enter a Value less than or equal to 1000 for the Electric Equipment Power Increasion Percentage or less than or equal to 100 for the Electric Equipment Power Reduction Percentage.")
      return false
    elsif elecequip_power_change_percent == 0
      runner.registerInfo("No electric electric equipment power adjustment requested, but some life cycle costs may still be affected.")
    elsif elecequip_power_change_percent < 1 and elecequip_power_change_percent > -1
      runner.registerWarning("A Electric Equipment Power change Percentage of #{elecequip_power_change_percent} percent is abnormally low.")
    elsif elecequip_power_change_percent > 90 or elecequip_power_change_percent < -900
      runner.registerWarning("A Electric Equipment Power change Percentage of #{elecequip_power_change_percent} percent is abnormally high.")
    end
	
    #helper to make numbers pretty (converts 4125001.25641 to 4,125,001.26 or 4,125,001). The definition be called through this measure.
    def neat_numbers(number, roundto = 2) #round to 0 or 2)
      if roundto == 2
        number = sprintf "%.2f", number
      else
        number = number.round
      end
      #regex to add commas
      number.to_s.reverse.gsub(%r{([0-9]{3}(?=([0-9])))}, "\\1,").reverse
    end #end def neat_numbers

    #helper to make it easier to do unit conversions on the fly.  The definition be called through this measure.
    def unit_helper(number,from_unit_string,to_unit_string)
      converted_number = OpenStudio::convert(OpenStudio::Quantity.new(number, OpenStudio::createUnit(from_unit_string).get), OpenStudio::createUnit(to_unit_string).get).get.value
    end

    #report initial condition
    building = model.getBuilding
    building_equip_power = building.electricEquipmentPower	
	
    # test if epd can be calculated, need alternative initial and final condition if it cannot
    building_EPD = nil
    begin
      building_EPD = building.electricEquipmentPowerPerFloorArea
      rescue
    end

    if not building_EPD.nil?
      building_EPD =  unit_helper(building.electricEquipmentPowerPerFloorArea,"W/m^2","W/ft^2")
      runner.registerInitialCondition("The model's initial building electric equipment power was  #{neat_numbers(building_equip_power,0)} watts, an electric equipment power density of #{neat_numbers(building_EPD)} w/ft^2.")
    else
      # can't calculate EPD, building may not have surfaces
      runner.registerInitialCondition("The model's initial building electric equipment power was  #{neat_numbers(building_equip_power,0)} watts.")
    end

    #get space types in model
    space_types = model.getSpaceTypes
	
    #def to alter performance and life cycle costs of objects
	object = model.getSpaceTypes
    def alter_performance(object, elecequip_power_change_percent, runner)

      #edit clone based on percentage reduction
      new_def = object
      if not new_def.designLevel.empty?
        new_electric_equipment_level = new_def.setDesignLevel(new_def.designLevel.get - new_def.designLevel.get*elecequip_power_change_percent*0.01)
      elsif not new_def.wattsperSpaceFloorArea.empty?
        new_electric_equipment_per_area = new_def.setWattsperSpaceFloorArea(new_def.wattsperSpaceFloorArea.get - new_def.wattsperSpaceFloorArea.get*elecequip_power_change_percent*0.01)
      elsif not new_def.wattsperPerson.empty?
        new_electric_equipment_per_person = new_def.setWattsperPerson(new_def.wattsperPerson.get - new_def.wattsperPerson.get*elecequip_power_change_percent*0.01)
      else
        runner.registerWarning("'#{new_def.name}' is used by one or more instances and has no load values. Its performance was not altered.")
      end
    end

    #make a hash of old defs and new electric equipment defs
    cloned_elecequip_defs = {}

    #loop through space types
    space_types.each do |space_type|
      next if not space_type.spaces.size > 0
      space_type_equipments = space_type.electricEquipment
      space_type_equipments.each do |space_type_equipment|
      
        new_def = nil

        #clone def if it has not already been cloned
        exist_def = space_type_equipment.electricEquipmentDefinition
        if not cloned_elecequip_defs[exist_def.name.get.to_s].nil?
          new_def = cloned_elecequip_defs[exist_def.name.get.to_s]
        else
          #clone rename and add to hash
          new_def = exist_def.clone(model)
          new_def_name = new_def.setName("#{exist_def.name.get} - #{elecequip_power_change_percent} percent reduction")
          new_def = new_def.to_ElectricEquipmentDefinition.get
          cloned_elecequip_defs[exist_def.name.get.to_s] = new_def

          #call def to alter performance and life cycle costs
          alter_performance(new_def, elecequip_power_change_percent, runner)

        end #end if cloned_elecequip_defs.any?
		
        #link instance with clone and rename
        updated_instance = space_type_equipment.setElectricEquipmentDefinition(new_def.to_ElectricEquipmentDefinition.get)
        updated_instance_name = space_type_equipment.setName("#{space_type_equipment.name} #{elecequip_power_change_percent} percent reduction")

      end #end space_type_equipments.each do

    end #end space types each do

    #get spaces in the model
    spaces = model.getSpaces

    spaces.each do |space|
      space_equipments = space.electricEquipment
      space_equipments.each do |space_equipment|

        #clone def if it has not already been cloned
        exist_def = space_equipment.electricEquipmentDefinition
        if not cloned_elecequip_defs[exist_def.name.get.to_s].nil?
          new_def = cloned_elecequip_defs[exist_def.name.get.to_s]
        else
          #clone rename and add to hash
          new_def = exist_def.clone(model)
          new_def_name = new_def.setName("#{new_def.name} - #{elecequip_power_change_percent} percent reduction")
          cloned_elecequip_defs[exist_def.name.get] = new_def
          new_def = new_def.to_ElectricEquipmentDefinition.get
		  
          #call def to alter performance and life cycle costs
          alter_performance(new_def, elecequip_power_change_percent, runner)

        end #end if cloned_elecequip_defs.any?

        #link instance with clone and rename
        updated_instance = space_equipment.setElectricEquipmentDefinition(new_def.to_ElectricEquipmentDefinition.get)
        updated_instance_name = space_equipment.setName("#{space_equipment.name} #{elecequip_power_change_percent} percent reduction")

      end #end space_equipment.each do

    end #end of loop through spaces

    if cloned_elecequip_defs.size == 0
      runner.registerAsNotApplicable("No electric equipment objects were found in the specified space type(s).")
    end

    #report final condition
    final_building = model.getBuilding
    final_building_equip_power = final_building.electricEquipmentPower

    # added if statement to have alt path if can't calculate lpd
    if not building_EPD.nil?
      final_building_EPD =  unit_helper(final_building.electricEquipmentPowerPerFloorArea,"W/m^2","W/ft^2")
      runner.registerFinalCondition("The model's final building electric equipment power was  #{neat_numbers(final_building_equip_power,0)} watts, an electric equipment power density of #{neat_numbers(final_building_EPD)} w/ft^2.")
    else
      runner.registerFinalCondition("The model's final building electric equipment power was  #{neat_numbers(final_building_equip_power,0)} watts.")
    end

    return true

  end #end the run method

end #end the measure

#this allows the measure to be used by the application
ChangeElectricEquipmentLoadsByPercentage.new.registerWithApplication	
