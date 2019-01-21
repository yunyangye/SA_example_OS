#start the measure
class ChangeOutdoorAir < OpenStudio::Ruleset::ModelUserScript
  
  #define the name that a user will see, this method may be deprecated as
  #the display name in PAT comes from the name field in measure.xml
  def name
    return "Change Outdoor Air"
  end

  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new

    #make an argument for reduction percentage
    design_spec_outdoor_air_per_person = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("design_spec_outdoor_air_per_person",true)
    design_spec_outdoor_air_per_person.setDisplayName("Design Specification Outdoor Air Flow per Person (ft3/min-person).")
    design_spec_outdoor_air_per_person.setDefaultValue(0.0)
    args << design_spec_outdoor_air_per_person

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
    design_spec_outdoor_air_per_person = runner.getDoubleArgumentValue("design_spec_outdoor_air_per_person",user_arguments)

    #check the design_spec_outdoor_air_per_person and design_spec_outdoor_air_per_area for reasonableness
    if design_spec_outdoor_air_per_person > 50 or design_spec_outdoor_air_per_person < 0
      runner.registerError("Please enter a value >=0 and <= 50 for the Outdoor Air Flow per Person.")
      return false
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

    #helper to make it easier to do unit conversions on the fly
    def unit_helper(number,from_unit_string,to_unit_string)
      converted_number = OpenStudio::convert(OpenStudio::Quantity.new(number, OpenStudio::createUnit(from_unit_string).get), OpenStudio::createUnit(to_unit_string).get).get.value
    end

    #convert arguments to si for future use
    design_spec_outdoor_air_per_person_si = unit_helper(design_spec_outdoor_air_per_person, "ft^3/min","m^3/s")
	
    #get space design_spec_outdoor_air_objects objects used in the model
    design_spec_outdoor_air_objects = model.getDesignSpecificationOutdoorAirs
    #todo - it would be nice to give ranges for different calculation methods but would take some work.

    #counters needed for measure
    altered_instances = 0

    #reporting initial condition of model
    if design_spec_outdoor_air_objects.size > 0
      runner.registerInitialCondition("The initial model contained #{design_spec_outdoor_air_objects.size} design specification outdoor air objects.")
    else
      runner.registerInitialCondition("The initial model did not contain any design specification outdoor air.")
    end

    #get space types in model
    building = model.building.get
    space_types = model.getSpaceTypes
    affected_area_si = building.floorArea

    #split apart any shared uses of design specification outdoor air
    design_spec_outdoor_air_objects.each do |design_spec_outdoor_air_object|
      direct_use_count = design_spec_outdoor_air_object.directUseCount
      next if not direct_use_count > 1
      direct_uses = design_spec_outdoor_air_object.sources
      original_cloned = false

      #adjust count test for direct uses that are component data
      direct_uses.each do |direct_use|
        component_data_source = direct_use.to_ComponentData
        if not component_data_source.empty?
          direct_use_count = direct_use_count -1
        end
      end
      next if not direct_use_count > 1

      direct_uses.each do |direct_use|

        #clone and hookup design spec OA
        space_type_source = direct_use.to_SpaceType
        if not space_type_source.empty?
          space_type_source = space_type_source.get
          cloned_object = design_spec_outdoor_air_object.clone
          space_type_source.setDesignSpecificationOutdoorAir(cloned_object.to_DesignSpecificationOutdoorAir.get)
          original_cloned = true
        end

        space_source = direct_use.to_Space
        if not space_source.empty?
          space_source = space_source.get
          cloned_object = design_spec_outdoor_air_object.clone
          space_source.setDesignSpecificationOutdoorAir(cloned_object.to_DesignSpecificationOutdoorAir.get)
          original_cloned = true
        end

      end #end of direct_uses.each do

      #delete the now unused design spec OA
      if original_cloned
        runner.registerInfo("Making shared object #{design_spec_outdoor_air_object.name} unique.")
        design_spec_outdoor_air_object.remove
      end

    end #end of design_spec_outdoor_air_objects.each do

    #def to alter performance and life cycle costs of objects
    def alter_performance(object, design_spec_outdoor_air_per_person_si, runner)

      #edit instance based on percentage reduction
      instance = object

      #not checking if fields are empty because these are optional like values for space infiltration are.
      new_outdoor_air_per_person = instance.setOutdoorAirFlowperPerson(design_spec_outdoor_air_per_person_si)

    end #end of def alter_performance()

    #array of instances to change
    instances_array = []

    #loop through space types
    space_types.each do |space_type|
      next if not space_type.spaces.size > 0
      instances_array << space_type.designSpecificationOutdoorAir
    end #end space types each do

    #get spaces in model
    spaces = model.getSpaces

    spaces.each do |space|
      instances_array << space.designSpecificationOutdoorAir
    end #end of loop through spaces

    instance_processed = []

    instances_array.each do |instance|

      next if instance.empty?
      instance = instance.get

      #only continue if this instance has not been processed yet
      next if instance_processed.include? instance
      instance_processed << instance

      #call def to alter performance
      alter_performance(instance, design_spec_outdoor_air_per_person_si, runner)

      #rename
      updated_instance_name = instance.setName("#{instance.name} (#{design_spec_outdoor_air_per_person} ft3/min-person")
      altered_instances += 1

    end

    if altered_instances == 0
      runner.registerAsNotApplicable("No design specification outdoor air objects were found in the specified space type(s).")
    end

    #report final condition
    affected_area_ip = OpenStudio::convert(affected_area_si,"m^2","ft^2").get
    runner.registerFinalCondition("#{altered_instances} design specification outdoor air objects in the model were altered affecting #{neat_numbers(affected_area_ip,0)}(ft^2).")

    return true

  end #end the run method

end #end the measure

#this allows the measure to be use by the application
ChangeOutdoorAir.new.registerWithApplication