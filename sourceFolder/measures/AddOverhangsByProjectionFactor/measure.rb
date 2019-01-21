# see the URL below for information on how to write OpenStudio measures
# http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/

#start the measure
class AddOverhangsByProjectionFactor < OpenStudio::Ruleset::ModelUserScript

  #define the name that a user will see
  def name
    return "Add Overhangs by Projection Factor"
  end

  # human readable description
  def description
    return "This measure aims to add overhangs using projection factor."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Add overhangs using projection factor (All directions are added)."
  end  
  
  #define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new

    #make an argument for projection factor
    projection_factor = OpenStudio::Ruleset::OSArgument::makeDoubleArgument("projection_factor",true)
    projection_factor.setDisplayName("Projection Factor (overhang depth / window height)")
    projection_factor.setDefaultValue(0.5)
    args << projection_factor

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
    projection_factor = runner.getDoubleArgumentValue("projection_factor",user_arguments)

    #check reasonableness of fraction
    projection_factor_too_small = false
    if projection_factor < 0
      runner.registerError("Please enter a positive number for the projection factor.")
      return false
    elsif projection_factor < 0.1
      runner.registerWarning("The requested projection factor of #{projection_factor} seems unusually small, no overhangs will be added.")
      projection_factor_too_small = true
    elsif projection_factor > 5
      runner.registerWarning("The requested projection factor of #{projection_factor} seems unusually large.")
    end

    #reporting initial condition of model
    number_of_exist_space_shading_surf = 0
    shading_groups = model.getShadingSurfaceGroups
    shading_groups.each do |shading_group|
      if shading_group.shadingSurfaceType == "Space"
        number_of_exist_space_shading_surf = number_of_exist_space_shading_surf + shading_group.shadingSurfaces.size
      end
    end
    runner.registerInitialCondition("The initial building had #{number_of_exist_space_shading_surf} space shading surfaces.")

    #construction_args = model.getConstructions	
	#construction_args.each do |x|
	#  if x.name.to_s.include? "Wall"
	#    construction = construction_args
	#	break
    #  end
	#end
	
    #delete all space shading groups if requested
    if number_of_exist_space_shading_surf > 0
      num_removed = 0
      shading_groups.each do |shading_group|
        if shading_group.shadingSurfaceType == "Space"
          shading_group.remove
          num_removed += 1
        end
      end
      runner.registerInfo("Removed all #{num_removed} space shading surface groups from the model.")
    end

    #flag for not applicable
    overhang_added = false

    #loop through surfaces finding exterior walls with proper orientation
    sub_surfaces = model.getSubSurfaces
    sub_surfaces.each do |s|

      next if not s.outsideBoundaryCondition == "Outdoors"
      next if s.subSurfaceType == "Skylight"
      next if s.subSurfaceType == "Door"
      next if s.subSurfaceType == "GlassDoor"
      next if s.subSurfaceType == "OverheadDoor"
      next if s.subSurfaceType == "TubularDaylightDome"
      next if s.subSurfaceType == "TubularDaylightDiffuser"

      #delete existing overhang for this window if it exists from previously run measure
      shading_groups.each do |shading_group|
        shading_s = shading_group.shadingSurfaces
        shading_s.each do |ss|
          if ss.name.to_s == "#{s.name.to_s} - Overhang"
            ss.remove
            runner.registerWarning("Removed pre-existing window shade named '#{ss.name}'.")
          end
        end
      end

      if projection_factor_too_small
        # new overhang would be too small and would cause errors in OpenStudio
        # don't actually add it, but from the measure's perspective this worked as requested
        overhang_added = true
      else
        # add the overhang
        new_overhang = s.addOverhangByProjectionFactor(projection_factor, 0)
        if new_overhang.empty?
          ok = runner.registerWarning("Unable to add overhang to " + s.briefDescription +
                   " with projection factor " + projection_factor.to_s + " and offset " + offset.to_s + ".")
          return false if not ok
        else
          new_overhang.get.setName("#{s.name} - Overhang")
          runner.registerInfo("Added overhang " + new_overhang.get.briefDescription + " to " +
              s.briefDescription + " with projection factor " + projection_factor.to_s +
              " and offset " + "0" + ".")
        #  new_overhang.get.setConstruction(construction)        
          overhang_added = true
        end
      end

    end #end sub_surfaces.each do |s|

    if not overhang_added
      runner.registerAsNotApplicable("The model has exterior #{facade.downcase} walls, but no windows were found to add overhangs to.")
      return true
    end

    #reporting final condition of model
    number_of_final_space_shading_surf = 0
    final_shading_groups = model.getShadingSurfaceGroups
    final_shading_groups.each do |shading_group|
      number_of_final_space_shading_surf = number_of_final_space_shading_surf + shading_group.shadingSurfaces.size
    end
    runner.registerFinalCondition("The final building has #{number_of_final_space_shading_surf} space shading surfaces.")

    return true

  end #end the run method

end #end the measure

#this allows the measure to be used by the application
AddOverhangsByProjectionFactor.new.registerWithApplication