bl_info = {
    "name": "Copy Object Animation to Bone Animation",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > Copy Object Animation to Bone Animation",
    "description": "Copy object's animation over to bone animation",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy, mathutils 
from bpy.types import Panel
from mathutils import Vector 

class COPY_OBJECT_ANIMATION_TO_BONE_ANIMATION_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Copy Object Animation to Bone Animation"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("object.copy_animation_to_bone", text="Run")
        col.prop(context.scene, "join_objects")
        col.prop(context.scene, "combine_armatures")
        col.prop(context.scene, "copy_location")
        col.prop(context.scene, "copy_rotation")
        col.prop(context.scene, "copy_scale")

class COPY_OBJECT_ANIMATION_TO_BONE_ANIMATION_OT_operator(bpy.types.Operator):
    bl_idname = "object.copy_animation_to_bone"
    bl_label = "Copy Object Animation to Bone Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        join_objects = context.scene.join_objects
        combine_armatures = context.scene.combine_armatures
        copy_location = context.scene.copy_location
        copy_rotation = context.scene.copy_rotation
        copy_scale = context.scene.copy_scale


        armatures = []
        #vertex_groups = {}
        mods = []
        objs = context.selected_objects

        for obj in objs:
            if obj.type != 'MESH':
                continue

            # Create armature and bone
            armature = bpy.data.armatures.new(obj.name + "_armature")
            armature_obj = bpy.data.objects.new(obj.name + "_armature_obj", armature)
            bpy.context.scene.collection.objects.link(armature_obj)
            
            #Setting the armature as active object
            bpy.context.view_layer.objects.active = armature_obj
            
            #Entering Edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            
            #adding the bone
            bone_name = str(obj.name + "_bone")
            edbone = armature.edit_bones.new("%s"%bone_name)
            edbone.head = Vector((0.0, 0.0, 0.0))
            edbone.tail = Vector((0.0, 1.0, 0.0))
            edbone.roll = 0 
    
            
            #Exiting Edit mode
            bpy.ops.object.mode_set(mode='OBJECT')
            armature_obj.show_in_front = True


            bpy.ops.object.mode_set(mode='POSE')
            
            bone = bpy.context.object.data.bones["%s"%bone_name]
            bpy.context.object.data.bones.active = bone
            bpy.context.object.data.bones.active.select = True

            
            # Copy animation
            if copy_location:
                bpy.ops.pose.constraint_add(type='COPY_LOCATION')
                bpy.context.object.pose.bones["%s"%bone_name].constraints["Copy Location"].target = obj
                #bpy.context.object.pose.bones["%s"%bone_name].constraints["Copy Location"].head_tail = 0
            if copy_rotation:
                bpy.ops.pose.constraint_add(type='COPY_ROTATION')
                bpy.context.object.pose.bones["%s"%bone_name].constraints["Copy Rotation"].target = obj
            if copy_scale:
                bpy.ops.pose.constraint_add(type='COPY_SCALE')
                bpy.context.object.pose.bones["%s"%bone_name].constraints["Copy Scale"].target = obj


            bpy.ops.object.mode_set(mode='OBJECT')

            # Assign vertices to new vertex group
            vertex_group = obj.vertex_groups.new(name=bone_name)
            for vert in obj.data.vertices:
                vertex_group.add([vert.index], 1.0, 'ADD')


            
            # Create armature modifier
            #armature_obj.data.pose_position = 'REST'
            #obj.parent = armature_obj
            #obj.parent_type = 'ARMATURE'


            #bpy.context.scene.frame_set(bpy.context.scene.frame_current)
            
            armatures.append(armature_obj)
            #vertex_groups[obj.name] = vertex_group


        # Combine all armatures into one
        #bpy.ops.object.select_all(action='DESELECT')
            #for arm in armatures:
                #arm.select_set(True)
                #context.view_layer.objects.active = arm

        bpy.ops.object.select_all(action='DESELECT')

                
        if combine_armatures:
            for arm in armatures:
                arm.select_set(True)
                context.view_layer.objects.active = arm
            bpy.ops.object.join()
            bpy.ops.nla.bake(frame_start = bpy.context.scene.frame_start, frame_end = bpy.context.scene.frame_end, only_selected=False, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})
            parent_arm = context.view_layer.objects.active
            armatures.clear()
            armatures.append(parent_arm)
            parent_arm.data.pose_position = 'REST'
            # Parent object to armature
            for obj in objs:
                if obj.rigid_body:
                    context.view_layer.objects.active = obj
                    bpy.ops.rigidbody.object_remove()
                    #bpy.context.collection.rigidbody_world.collection.objects.unlink(obj)
                if copy_location:
                    obj.location = [0,0,0]
                if copy_rotation:
                    obj.rotation_euler = [0,0,0]
                if copy_scale:
                    obj.scale = [1,1,1]
                obj.parent = parent_arm
                obj.parent_type = 'OBJECT'
            parent_arm.data.pose_position = 'POSE'

        else:
            for arm in armatures:
                arm.select_set(True)
                bpy.ops.nla.bake(frame_start = bpy.context.scene.frame_start, frame_end = bpy.context.scene.frame_end, only_selected=False, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})
                arm.data.pose_position = 'REST'
                # Parent object to armature
            for obj in objs:
                if obj.rigid_body:
                    context.view_layer.objects.active = obj
                    bpy.ops.rigidbody.object_remove()
                    #bpy.context.collection.rigidbody_world.collection.objects.unlink(obj)
                if copy_location:
                    obj.location = [0,0,0]
                if copy_rotation:
                    obj.rotation_euler = [0,0,0]
                if copy_scale:
                    obj.scale = [1,1,1]
                obj.parent = arm
                obj.parent_type = 'OBJECT'
            for arm in armatures:
                arm.data.pose_position = 'POSE'
                
                    #arm.data.pose_position = 'POSE'


        # Clear object animation
        #bpy.ops.object.select_all(action='DESELECT')
        for obj in objs:
            obj.animation_data_clear()
            if copy_location:
                obj.location = [0,0,0]
            if copy_rotation:
                obj.rotation_euler = [0,0,0]
            if copy_scale:
                obj.scale = [1,1,1]
            armature_mod = obj.modifiers.new(type='ARMATURE', name='ConvertToBone')
            armature_mod.object = obj.parent
            #armature_mod.show_viewport = False
            #obj.modifiers['ConvertToBone'].show_viewport = True
            #context.view_layer.objects.active = obj
            #obj.select_set(False)
            if join_objects:
                context.view_layer.objects.active = obj
                obj.select_set(True)
        if join_objects:
            bpy.ops.object.join()
            

        """

        #if combine_armatures:
        #for arm in armatures:
            #armatures[0].data.pose_position = 'POSE'
            #arm.select_set(False)
            

        #for mod in mods:
            #mod.show_viewport = True

        #bpy.ops.object.select_all(action='DESELECT')

        """

        return {'FINISHED'}

def register():
    bpy.utils.register_class(COPY_OBJECT_ANIMATION_TO_BONE_ANIMATION_PT_panel)
    bpy.utils.register_class(COPY_OBJECT_ANIMATION_TO_BONE_ANIMATION_OT_operator)
    bpy.types.Scene.join_objects = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.combine_armatures = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.copy_location = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.copy_rotation = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.copy_scale = bpy.props.BoolProperty(default=True)

def unregister():
    bpy.utils.unregister_class(COPY_OBJECT_ANIMATION_TO_BONE_ANIMATION_PT_panel)
    bpy.utils.unregister_class(COPY_OBJECT_ANIMATION_TO_BONE_ANIMATION_OT_operator)
    del bpy.types.Scene.join_objects
    del bpy.types.Scene.combine_armatures
    del bpy.types.Scene.copy_location
    del bpy.types.Scene.copy_rotation
    del bpy.types.Scene.copy_scale

if __name__ == "__main__":
    register()